"""
Script to refresh ChromaDB with updated knowledge base

Usage:
    python refresh_chromadb.py

Description:
    This script will:
    1. Delete the old ChromaDB collection
    2. Read the latest Project_Documents.md
    3. Generate new embeddings using Azure OpenAI
    4. Create a new collection with updated data

Run this script whenever you update Project_Documents.md
"""
import chromadb
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

print("=" * 70)
print("🔄 CHROMADB KNOWLEDGE BASE REFRESH UTILITY")
print("=" * 70)
print("\n⚠️  This will DELETE the existing ChromaDB collection and recreate it.")
print("📝 Make sure you have updated Project_Documents.md first.\n")

# Confirmation prompt
try:
    confirm = input("Do you want to continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("\n❌ Operation cancelled by user.")
        sys.exit(0)
except KeyboardInterrupt:
    print("\n\n❌ Operation cancelled by user.")
    sys.exit(0)

print("\n" + "=" * 70)
print("STARTING REFRESH PROCESS...")
print("=" * 70)

# Initialize OpenAI client
print("\n1. Initializing OpenAI client...")
client = OpenAI(
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
)
print("   ✓ OpenAI client initialized")

# Connect to ChromaDB
print("\n2. Connecting to ChromaDB...")
# ChromaDB path should be in src/local_chromadb (go up from tools to src, then to local_chromadb)
chroma_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_chromadb")
chroma_client = chromadb.PersistentClient(path=chroma_path)
print("   ✓ Connected to ChromaDB")

# Delete old collection
print("\n3. Deleting old collection...")
try:
    chroma_client.delete_collection("it_help_desk_kb")
    print("   ✓ Old collection deleted")
except:
    print("   ℹ Collection doesn't exist, creating new one")

# Create new collection
print("\n4. Creating new collection...")
collection = chroma_client.get_or_create_collection(
    name="it_help_desk_kb",
    metadata={"hnsw:space": "cosine"}
)
print("   ✓ New collection created")

# Load knowledge base from markdown file
print("\n5. Loading knowledge base from Project_Documents.md...")
# Get the path to src/docs/Project_Documents.md (go up from tools to src, then to docs)
kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "Project_Documents.md")

with open(kb_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

kb_data = []
current_category = "General"
question = None
current_section = ""

for line in lines:
    line_stripped = line.strip()
    
    # Detect sections
    if line_stripped.startswith('## 📞'):
        current_section = "contact_info"
        # Add entire contact section as one document
        contact_text = ""
        continue
    elif line_stripped.startswith('## 📋'):
        current_section = "qa"
        continue
    elif line_stripped.startswith('## 🔧'):
        current_section = "resources"
        # Add entire resources section as one document
        resources_text = ""
        continue
    
    # Handle contact info section
    if current_section == "contact_info" and line_stripped and not line_stripped.startswith('---'):
        if 'contact_text' not in locals():
            contact_text = ""
        contact_text += line_stripped + "\n"
        if line_stripped.startswith('**Thời gian phản hồi:**'):
            # Continue collecting until end of section
            pass
    elif current_section == "contact_info" and line_stripped.startswith('---'):
        if 'contact_text' in locals() and contact_text:
            kb_data.append({
                "text": f"Thông tin liên hệ IT Support:\n{contact_text}",
                "metadata": {"category": "contact_info"}
            })
            del contact_text
    
    # Handle Q&A section
    if current_section == "qa":
        if line_stripped.startswith('**Q'):
            question = line_stripped.split('.', 1)[1].replace("**", "").strip() if '.' in line_stripped else line_stripped.replace("**", "").strip()
        elif line_stripped.startswith('A'):
            answer_parts = line_stripped.split(':', 1)
            if len(answer_parts) > 1:
                answer = answer_parts[1].strip()
                if question:
                    full_text = f"Question: {question}\nAnswer: {answer}"
                    kb_data.append({
                        "text": full_text,
                        "metadata": {"category": "qa"}
                    })
                    question = None
    
    # Handle resources section
    if current_section == "resources" and line_stripped and not line_stripped.startswith('---') and not line_stripped.startswith('_Last Update'):
        if 'resources_text' not in locals():
            resources_text = ""
        resources_text += line_stripped + "\n"

# Add resources section at the end
if 'resources_text' in locals() and resources_text:
    kb_data.append({
        "text": f"Tài nguyên & Hệ thống nội bộ:\n{resources_text}",
        "metadata": {"category": "resources"}
    })

print(f"   ✓ Loaded {len(kb_data)} records")

# Generate embeddings and add to ChromaDB
print("\n6. Generating embeddings and adding to ChromaDB...")
documents = []
metadatas = []
ids = []

for i, item in enumerate(kb_data):
    documents.append(item["text"])
    metadatas.append(item["metadata"])
    ids.append(f"doc_{i}")

# Generate embeddings in batch
try:
    response = client.embeddings.create(
        input=documents,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    )
    embeddings = [item.embedding for item in response.data]
    print(f"   ✓ Generated {len(embeddings)} embeddings")
except Exception as e:
    print(f"   ✗ Error generating embeddings: {e}")
    exit(1)

# Add to collection
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids,
    embeddings=embeddings
)
print(f"   ✓ Added {len(documents)} documents to ChromaDB")

# Verify
print("\n7. Verifying data...")
count = collection.count()
print(f"   ✓ Total documents in DB: {count}")

# Test search with contact info
print("\n8. Testing search for contact information...")
test_query = "số điện thoại hotline hỗ trợ IT"
response = client.embeddings.create(
    input=test_query,
    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
)
query_embedding = response.data[0].embedding

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)

if results and results.get('documents') and results['documents'][0]:
    doc = results['documents'][0][0]
    print(f"   Query: '{test_query}'")
    print(f"   Result: {doc[:200]}...")
    print("   ✓ Contact info search working!")
else:
    print("   ✗ No results found")

print("\n" + "=" * 70)
print("✅ CHROMADB REFRESH COMPLETED SUCCESSFULLY!")
print("=" * 70)
print(f"\n📊 Summary:")
print(f"   - Total documents: {count}")
print(f"   - Categories: contact_info, qa, resources")
print(f"   - Database location: src/local_chromadb/")
print(f"\n💡 Next steps:")
print(f"   - Test the chatbot: python test/test_chatbot_contact.py")
print(f"   - Start the app: python main.py")
print(f"\n📖 For more info, see: CHROMADB_UPDATE_GUIDE.md")
print("=" * 70)
