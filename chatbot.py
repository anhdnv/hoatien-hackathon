from langchain.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_tavily import TavilySearch
from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, VectorType
from openai import OpenAI
import os
from datetime import datetime
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from tts_service import tts_service
from langdetect import detect, LangDetectException

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
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        
        # Create or get existing index
        try:
            self.index = self.pc.Index(name=self.index_name)
        except Exception:
            # Create new index if it doesn't exist
            index_config = self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # For Azure OpenAI ada-002
                spec=ServerlessSpec(
                    cloud=CloudProvider.AWS,
                    region=AwsRegion.US_EAST_1
                ),
                vector_type=VectorType.DENSE
            )
            self.index = self.pc.Index(host=index_config.host)

        # Initialize Tavily Search for web search
        self.search_tool = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))

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
        """Initialize the knowledge base with IT support information from JSON file"""
        try:
            with open("knowledge_base.json", "r") as f:
                kb_data = json.load(f)["records"]
            logger.info(f"Loaded {len(kb_data)} records from knowledge base file")
        except FileNotFoundError:
            logger.error("Knowledge base file not found. Using default records.")
            kb_data = [
                {
                    "text": "To reset your password: 1. Visit the password reset portal 2. Click 'Forgot Password' 3. Follow the instructions sent to your email",
                    "metadata": {"category": "password_reset"}
                }
            ]
        except json.JSONDecodeError:
            logger.error("Error parsing knowledge base file. Using default records.")
            kb_data = [
                {
                    "text": "To reset your password: 1. Visit the password reset portal 2. Click 'Forgot Password' 3. Follow the instructions sent to your email",
                    "metadata": {"category": "password_reset"}
                }
            ]

        try:
            # Create vectors for each document
            vectors = []
            for i, item in enumerate(kb_data):
                # Generate embedding for the text
                response = self.client.embeddings.create(
                    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
                    input=item["text"]
                )
                embedding = response.data[0].embedding
                
                # Prepare vector tuple (id, embedding, metadata)
                vector = (
                    f"doc_{i}",  # unique ID
                    embedding,
                    {
                        "text": item["text"],  # original text
                        "category": item["metadata"]["category"]  # metadata
                    }
                )
                vectors.append(vector)
            
            # Upsert vectors to Pinecone index
            self.index.upsert(
                vectors=vectors,
                namespace="it-helpdesk"  # organize vectors in a namespace
            )
            logger.info("Knowledge base initialized in Pinecone")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            return None
        
    def load_knowledge_base(self):
        """Load the IT support knowledge base."""
        try:
            with open("knowledge_base.json", "r") as f:
                return json.load(f)
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
    


    def _detect_language(self, text: str) -> str:
        """
        Phát hiện ngôn ngữ của văn bản và trả về mã ngôn ngữ (ISO 639-1).
        Mặc định là 'vi' (Tiếng Việt) nếu không phát hiện được hoặc có lỗi.
        """
        if not text:
            return 'vi'
        
        try:
            # Phát hiện ngôn ngữ
            lang_code = detect(text)
            # Chuyển các mã ngôn ngữ đặc biệt sang mã chuẩn được gTTS hỗ trợ
            if lang_code == 'zh-cn':
                return 'zh'
            
            # GTTS đôi khi có vấn đề với Tiếng Việt, sử dụng 'vi' làm mặc định
            if lang_code in ['vi', 'en']:
                return lang_code
            else:
                # Trả về mã ngôn ngữ đã phát hiện
                return lang_code
            
        except LangDetectException:
            # Trả về mặc định nếu không phát hiện được ngôn ngữ
            return 'vi'
        except Exception as e:
            logger.warning(f"Lỗi khi phát hiện ngôn ngữ: {e}")
            return 'vi'
    
    def get_response(self, user_input: str, enable_tts: bool = False) -> Dict[str, Any]:
        """Generate a response based on user input with optional TTS."""
        try:
            # Add user message to conversation history
                self.conversation_history.append(
                    Message(
                        role="user",
                        content=user_input,
                        timestamp=datetime.now().isoformat()
                    )
                )
            
                # First try to get answer from Pinecone knowledge base
                kb_answer = self.check_knowledge_base(user_input)
                
                # If no relevant answer from knowledge base, use Tavily Search
                if not kb_answer:
                    try:
                        logger.info(f"Calling search_tool with query: {user_input}")
                        search_results = self.search_tool.invoke(user_input)
                        logger.info(f"Search results received: {search_results}")
                        
                        if search_results and isinstance(search_results, str):
                            context = search_results
                        else:
                            context = ""
                    except Exception as e:
                        logger.error(f"Search error: {str(e)}")
                        context = ""
                else:
                    context = f"From knowledge base: {kb_answer}"                # Generate response using LLM with search results as context
                messages = [
                    {"role": "system", "content": "You are an IT Help Desk assistant. Use the following context from web search to help answer the user's question."},
                    {"role": "user", "content": f"Context from search: {context}\n\nUser question: {user_input}"}
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
        
        # Generate TTS audio if requested
        audio_url = None
        if enable_tts and response_content:
            try:
                detected_lang = self._detect_language(response_content)
                logger.info(f"Ngôn ngữ được phát hiện cho TTS: {detected_lang}")
                audio_path = tts_service.text_to_speech(response_content, lang=detected_lang, speed=2)
                if audio_path:
                    audio_url = tts_service.get_audio_url(audio_path)
                    # Cleanup old audio files
                    tts_service.cleanup_old_audio()
            except Exception as e:
                logger.error(f"Error generating TTS: {str(e)}")
        
        return {
            "response": response_content,
            "audio_url": audio_url
        }
    
    def check_knowledge_base(self, user_input: str) -> Optional[str]:
        """
        Thực hiện tìm kiếm ngữ nghĩa trong ChromaDB cho câu trả lời nhanh.
        Sử dụng RAG (Retrieval-Augmented Generation) nếu cần.
        """
        if not self.knowledge_base_collection:
            return None
        
        try:
            results = self.knowledge_base_collection.query(
                query_texts=[user_input],
                n_results=1
            )
            
            if results and results.get('documents') and results['documents'][0]:
                document = results['documents'][0][0]
                distance = results['distances'][0][0] if results.get('distances') else 0.0
                
                relevance_threshold = 0.4
                
                if distance < relevance_threshold:
                    logger.info(f"Quick response from KB found (Distance: {distance:.4f})")
                    return document
                else:
                    logger.info(f"Found context, but low relevance (Distance: {distance:.4f}). Will pass to LLM.")
                    context_message = f"**CONTEXT from KB:**\n{document}\n"
                    
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking knowledge base with ChromaDB: {str(e)}")
            return None
    
    def check_knowledge_base(self, query: str) -> Optional[str]:
        """Search the knowledge base using vector similarity."""
        try:
            # Generate query embedding
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = response.data[0].embedding
            
            # Query the index
            query_response = self.index.query(
                vector=query_embedding,
                top_k=1,
                include_metadata=True,
                namespace="it-helpdesk"
            )
            
            # Check if we got any matches
            if query_response.matches and len(query_response.matches) > 0:
                top_match = query_response.matches[0]
                
                # Check if the match is relevant enough
                if top_match.score >= 0.7:  # Adjust threshold as needed
                    return top_match.metadata.get("text")
            
            return None
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
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
