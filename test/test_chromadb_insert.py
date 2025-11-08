"""Script to test ChromaDB insert and retrieval"""
import chromadb
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

print("=" * 60)
print("CHROMADB INSERT AND RETRIEVAL TEST")
print("=" * 60)

# Initialize OpenAI client for embeddings
print("\n1. Initializing OpenAI client for embeddings...")
client = OpenAI(
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
)
print("   ✓ OpenAI client initialized")

# Connect to ChromaDB
print("\n2. Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="local_chromadb")
print("   ✓ Connected to ChromaDB")

# Get or create collection
print("\n3. Getting collection...")
collection = chroma_client.get_or_create_collection(
    name="it_help_desk_kb",
    metadata={"hnsw:space": "cosine"}
)
print(f"   ✓ Collection: {collection.name}")
print(f"   ✓ Current documents count: {collection.count()}")

# If empty, add some test documents
if collection.count() == 0:
    print("\n4. Collection is empty. Adding test documents...")
    
    test_docs = [
        {
            "text": "Question: How do I reset my password?\nAnswer: To reset your password, go to the login page and click 'Forgot Password'. Follow the instructions sent to your email.",
            "metadata": {"category": "password"}
        },
        {
            "text": "Question: How do I connect to VPN?\nAnswer: Download the VPN client from the IT portal. Install it and use your company credentials to connect.",
            "metadata": {"category": "network"}
        },
        {
            "text": "Question: My computer is running slow. What should I do?\nAnswer: First, close unnecessary programs. Check Task Manager for high CPU usage. Restart your computer if needed.",
            "metadata": {"category": "performance"}
        }
    ]
    
    documents = []
    metadatas = []
    ids = []
    embeddings = []
    
    for i, doc in enumerate(test_docs):
        documents.append(doc["text"])
        metadatas.append(doc["metadata"])
        ids.append(f"test_doc_{i}")
        
        # Generate embedding
        print(f"   - Generating embedding for document {i+1}/{len(test_docs)}...")
        response = client.embeddings.create(
            input=doc["text"],
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
        )
        embeddings.append(response.data[0].embedding)
    
    # Add to collection
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )
    print(f"   ✓ Added {len(test_docs)} documents to ChromaDB")
else:
    print("\n4. Collection already has documents. Skipping insert.")

# Test retrieval
print("\n5. Testing document retrieval...")
print(f"   Total documents in DB: {collection.count()}")

# Get all documents
all_docs = collection.get(limit=5)
print(f"\n   First {min(5, len(all_docs['ids']))} documents:")
for i, (doc_id, doc, meta) in enumerate(zip(all_docs['ids'], all_docs['documents'], all_docs['metadatas'])):
    print(f"\n   [{i+1}] ID: {doc_id}")
    print(f"       Category: {meta.get('category', 'N/A')}")
    print(f"       Content: {doc[:100]}...")

# Test semantic search
print("\n6. Testing semantic search...")
test_queries = [
    "I forgot my password",
    "How to connect VPN?",
    "Computer performance issue"
]

for query in test_queries:
    print(f"\n   Query: '{query}'")
    
    # Generate query embedding
    response = client.embeddings.create(
        input=query,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    )
    query_embedding = response.data[0].embedding
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )
    
    if results and results.get('documents') and results['documents'][0]:
        doc = results['documents'][0][0]
        distance = results['distances'][0][0] if results.get('distances') else 0.0
        print(f"   → Found (distance: {distance:.4f})")
        print(f"   → {doc[:150]}...")
    else:
        print("   → No results found")

print("\n" + "=" * 60)
print("TEST COMPLETED SUCCESSFULLY!")
print("=" * 60)
