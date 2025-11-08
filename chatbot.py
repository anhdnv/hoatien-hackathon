from langchain.tools import tool
from langchain_openai import AzureChatOpenAI
import chromadb
from openai import OpenAI
import os
from datetime import datetime
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    role: str
    content: str
    timestamp: str
    function_call: Optional[Dict] = None
    name: Optional[str] = None

class ITHelpDeskBot:
    def __init__(self):
        # Initialize Azure OpenAI
        self.llm = AzureChatOpenAI(
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT")
        )
        
        # Initialize OpenAI client for embeddings
        self.client = OpenAI(
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
        )
        
        # Initialize ChromaDB (local only) - using new PersistentClient API
        # Disable telemetry for privacy
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        
        self.chroma_client = chromadb.PersistentClient(path="local_chromadb")
        # Create collection without default embedding function (we'll handle embeddings ourselves)
        self.knowledge_base_collection = self.chroma_client.get_or_create_collection(
            name="it_help_desk_kb",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

        # Initialize knowledge base
        self._initialize_knowledge_base()

        # Initialize conversation history with system message
        self.conversation_history: List[Message] = [
            Message(
                role="system",
                content="You are an IT Help Desk assistant specialized in providing clear, concise solutions to technical problems. Use the available functions when appropriate.",
                timestamp=datetime.now().isoformat()
            )
        ]
        
        # Define available functions
        self.available_functions = {
            "check_system_status": self.check_system_status,
            "reset_password": self.reset_password,
            "create_ticket": self.create_ticket
        }
        
        self.message_batch = []
        self.batch_size = 5
        self.batch_timeout = 1.0  # seconds
        
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with IT support information from Markdown file"""
        try:
            # Construct absolute path to the knowledge base file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            kb_path = os.path.join(script_dir, "docs", "Project_Documents.md")
            
            with open(kb_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            kb_data = []
            current_category = "General"
            question = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('## '):
                    try:
                        # Extracts category from headers like "## 1. NETWORK INFORMATION"
                        category_text = line.split('.', 1)[1]
                        current_category = category_text.replace("INFORMATION", "").replace("=", "").strip()
                    except IndexError:
                        current_category = "General"
                elif line.startswith('**Q'):
                    question = line.split('.', 1)[1].replace("**", "").strip()
                elif line.startswith('A'):
                    # Handles answers that might be multi-line or have complex formatting
                    answer_parts = line.split(':', 1)
                    if len(answer_parts) > 1:
                        answer = answer_parts[1].strip()
                        if question:
                            # Combine question and answer for a complete entry
                            full_text = f"Question: {question}\nAnswer: {answer}"
                            kb_data.append({
                                "text": full_text,
                                "metadata": {"category": current_category}
                            })
                            # Log each entry for verification
                            logger.debug(f"Added to KB: {full_text}")
                            question = None  # Reset question after pairing
                    else:
                        # This could be a continuation of a previous answer
                        if kb_data:
                            kb_data[-1]["text"] += f"\n{line.strip()}"
                            logger.debug(f"Appended to last KB entry: {line.strip()}")

            logger.info(f"Loaded {len(kb_data)} records from knowledge base file")

        except FileNotFoundError:
            logger.error("Knowledge base file not found. Using default records.")
            kb_data = [
                {
                    "text": "To reset your password: 1. Visit the password reset portal 2. Click 'Forgot Password' 3. Follow the instructions sent to your email",
                    "metadata": {"category": "password_reset"}
                }
            ]
        except Exception as e:
            logger.error(f"Error parsing knowledge base file: {e}. Using default records.")
            kb_data = [
                {
                    "text": "To reset your password: 1. Visit the password reset portal 2. Click 'Forgot Password' 3. Follow the instructions sent to your email",
                    "metadata": {"category": "password_reset"}
                }
            ]

        try:
            # Check if collection already has documents
            existing_count = self.knowledge_base_collection.count()
            if existing_count > 0:
                logger.info(f"Knowledge base already initialized with {existing_count} documents")
                return
            
            # Create embeddings using Azure OpenAI and add to ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for i, item in enumerate(kb_data):
                documents.append(item["text"])
                metadatas.append(item["metadata"])
                ids.append(f"doc_{i}")
            
            # Generate embeddings in batch for better performance
            logger.info(f"Generating embeddings for {len(documents)} documents...")
            try:
                # Azure OpenAI can handle multiple inputs at once
                all_texts = [item["text"] for item in kb_data]
                response = self.client.embeddings.create(
                    input=all_texts,
                    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
                )
                embeddings = [item.embedding for item in response.data]
                logger.info(f"Successfully generated {len(embeddings)} embeddings")
            except Exception as e:
                logger.error(f"Error generating embeddings in batch: {str(e)}")
                # Fallback to individual generation
                embeddings = []
                for i, item in enumerate(kb_data):
                    try:
                        response = self.client.embeddings.create(
                            input=item["text"],
                            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
                        )
                        embeddings.append(response.data[0].embedding)
                        logger.info(f"Generated embedding {i+1}/{len(kb_data)}")
                    except Exception as e2:
                        logger.error(f"Error generating embedding for document {i}: {str(e2)}")
                        embeddings.append([0.0] * 1536)

            self.knowledge_base_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            logger.info(f"Knowledge base initialized in ChromaDB with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            return None
        
    def load_knowledge_base(self):
        """Load the IT support knowledge base."""
        try:
            with open("src/docs/Project_Documents.md", "r", encoding="utf-8") as f:
                # This function may need a more sophisticated Markdown parser
                # For now, we'll just return the raw content for potential use.
                return f.read()
        except FileNotFoundError:
            # Return default knowledge base if file doesn't exist
            return {
                "common_issues": {
                    "password_reset": {
                        "keywords": ["password", "reset", "forgot", "change"],
                        "solution": "To reset your password:\n1. Visit the password reset portal\n2. Click 'Forgot Password'\n3. Follow the instructions sent to your email"
                    },
                    "network_connectivity": {
                        "keywords": ["internet", "network", "wifi", "connection"],
                        "solution": "To resolve network issues:\n1. Check if WiFi is enabled\n2. Try disconnecting and reconnecting\n3. Restart your device\n4. Contact IT if issue persists"
                    }
                }
            }
    


    def get_response(self, user_input: str, language: str = "vi", enable_tts: bool = False) -> Dict[str, Any]:
        """Generate a response based on user input and selected language."""
        try:
            # Add user message to conversation history
            self.conversation_history.append(
                Message(
                    role="user",
                    content=user_input,
                    timestamp=datetime.now().isoformat()
                )
            )
            
            # First try to get answer from ChromaDB knowledge base
            kb_answer = self.check_knowledge_base(user_input)
            
            context = ""
            if kb_answer:
                context = f"From knowledge base: {kb_answer}"
            
            # Get few-shot examples
            few_shot_examples = self._get_few_shot_examples()
            
            # Set language instruction
            language_instruction = ""
            if language == "en":
                language_instruction = "IMPORTANT: You must respond in English only."
            else:  # vi
                language_instruction = "QUAN TRỌNG: Bạn phải trả lời bằng tiếng Việt."

            # Generate response using LLM with context and few-shot examples
            messages = [
                {"role": "system", "content": f"You are an IT Help Desk assistant. Use the following context to help answer the user's question. If the context is empty, use your general knowledge. Follow the examples provided.\n\n{language_instruction}"},
                *few_shot_examples,
                {"role": "user", "content": f"Context: {context}\n\nUser question: {user_input}"}
            ]
            response = self.llm.invoke(messages)
            response_content = response.content
            
            # Add response to conversation history
            response_message = Message(
                role="assistant", 
                content=response_content,
                timestamp=datetime.now().isoformat()
            )
            self.conversation_history.append(response_message)
            
            # Handle function calls if any
            if hasattr(response_message, 'function_call') and response_message.function_call:
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                
                if function_name in self.available_functions:
                    function_response = self.available_functions[function_name](**function_args)
                    response_content = f"I've {function_name.replace('_', ' ')}: {function_response}"
                else:
                    response_content = response_message.content
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            response_content = "I apologize, but I encountered an error while searching for information. Let me try to help based on my existing knowledge."
        
        # Add bot response to conversation history
        self.conversation_history.append(
            Message(
                role="assistant",
                content=response_content,
                timestamp=datetime.now().isoformat()
            )
        )
        
        return {
            "response": response_content,
            "audio_url": None
        }
    
    def _get_few_shot_examples(self) -> List[Dict[str, Any]]:
        """Provides few-shot examples to guide the LLM."""
        return [
            {"role": "user", "content": "How do I reset my password?"},
            {"role": "assistant", "content": "To reset your password: 1. Visit the password reset portal 2. Click 'Forgot Password' 3. Follow the instructions sent to your email"},
            {"role": "user", "content": "My computer is running very slow and I've already tried restarting it. Can you help?"},
            # This is a simplified representation of a function call for the prompt
            {"role": "assistant", "content": "I can create a support ticket for you. What is a brief description of the issue?"},
            {"role": "user", "content": "What's the weather like today?"},
            {"role": "assistant", "content": "I am an IT Help Desk assistant and cannot provide weather information. Please let me know if you have a technical issue."}
        ]
    
    def check_knowledge_base(self, user_input: str) -> Optional[str]:
        """
        Thực hiện tìm kiếm ngữ nghĩa trong ChromaDB cho câu trả lời nhanh.
        """
        try:
            # Generate embedding for the query using Azure OpenAI
            response = self.client.embeddings.create(
                input=user_input,
                model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
            )
            query_embedding = response.data[0].embedding
            
            # Query ChromaDB with the embedding
            results = self.knowledge_base_collection.query(
                query_embeddings=[query_embedding],
                n_results=1
            )
            
            if results and results.get('documents') and results['documents'][0]:
                document = results['documents'][0][0]
                distance = results['distances'][0][0] if results.get('distances') else 0.0
                logger.info(f"Found document in ChromaDB with distance: {distance:.4f}")
                return document
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking knowledge base with ChromaDB: {str(e)}")
            return None

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get the definitions of available functions for the API."""
        return [
            {
                "name": "check_system_status",
                "description": "Check the status of various IT systems",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "system": {
                            "type": "string",
                            "enum": ["network", "email", "servers", "vpn"],
                            "description": "The system to check"
                        }
                    },
                    "required": ["system"]
                }
            },
            {
                "name": "reset_password",
                "description": "Initiate a password reset for a user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "The username of the account"
                        },
                        "system": {
                            "type": "string",
                            "enum": ["email", "windows", "vpn"],
                            "description": "The system for password reset"
                        }
                    },
                    "required": ["username", "system"]
                }
            },
            {
                "name": "create_ticket",
                "description": "Create a new IT support ticket",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_type": {
                            "type": "string",
                            "enum": ["hardware", "software", "network", "access"],
                            "description": "The type of issue"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "The priority level of the issue"
                        },
                        "description": {
                            "type": "string",
                            "description": "Brief description of the issue"
                        }
                    },
                    "required": ["issue_type", "priority", "description"]
                }
            }
        ]
    
    def check_system_status(self, system: str) -> str:
        """Mock function to check system status."""
        # In a real implementation, this would check actual system status
        statuses = {
            "network": "Operational",
            "email": "Operational",
            "servers": "Operational",
            "vpn": "Operational"
        }
        return f"{system.capitalize()} system status: {statuses.get(system, 'Unknown')}"
    
    def reset_password(self, username: str, system: str) -> str:
        """Mock function to handle password reset requests."""
        # In a real implementation, this would integrate with actual password reset system
        return f"Password reset initiated for {username} on {system} system. Check your email for further instructions."
    
    def create_ticket(self, issue_type: str, priority: str, description: str) -> str:
        """Mock function to create support tickets."""
        # In a real implementation, this would create actual support tickets
        ticket_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return f"Ticket {ticket_id} created: {issue_type} issue, {priority} priority - {description}"
    
    def save_conversation(self):
        """Save the conversation history to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        
        # Convert Message objects to dictionaries
        history_dict = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "function_call": msg.function_call,
                "name": msg.name
            }
            for msg in self.conversation_history
        ]
        
        with open(filename, "w") as f:
            json.dump(history_dict, f, indent=2)
