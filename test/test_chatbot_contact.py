"""Quick test chatbot with contact info queries"""
import os
from dotenv import load_dotenv
from chatbot import ITHelpDeskBot

load_dotenv()

print("=" * 60)
print("TESTING CHATBOT WITH CONTACT INFO QUERIES")
print("=" * 60)

# Initialize bot
print("\nInitializing chatbot...")
bot = ITHelpDeskBot()
print("✓ Chatbot initialized")

# Test queries
test_queries = [
    "Số điện thoại hotline IT là gì?",
    "Email hỗ trợ IT là gì?",
    "Địa chỉ văn phòng IT ở đâu?",
    "VPN gateway là gì?",
    "Giờ làm việc của IT là khi nào?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"Query {i}: {query}")
    print("="*60)
    
    try:
        response = bot.get_response(query)
        print(f"\nResponse:\n{response['response']}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*60)
print("TEST COMPLETED")
print("="*60)
