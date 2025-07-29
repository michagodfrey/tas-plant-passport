#!/usr/bin/env python3
"""
Test script to verify the Gemini setup works correctly.
This script tests the basic functionality without requiring the full index.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test that we can connect to Gemini API."""
    try:
        # Check if API key is set
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        # Test basic Gemini connection
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            convert_system_message_to_human=True
        )
        
        # Simple test query
        response = llm.invoke("Say 'Hello from Gemini!'")
        print(f"✅ Gemini connection successful: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False

def test_openai_embeddings():
    """Test that OpenAI embeddings work (for vector search)."""
    try:
        # Check if API key is set
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        # Test OpenAI embeddings
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()
        
        # Simple test embedding
        test_text = "This is a test embedding"
        embedding = embeddings.embed_query(test_text)
        
        print(f"✅ OpenAI embeddings successful (vector length: {len(embedding)})")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI embeddings failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Gemini Setup...")
    print("=" * 50)
    
    # Test Gemini
    gemini_ok = test_gemini_connection()
    
    # Test OpenAI embeddings
    embeddings_ok = test_openai_embeddings()
    
    print("=" * 50)
    if gemini_ok and embeddings_ok:
        print("✅ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python tas_index.py")
        print("2. Run: python agent_setup_tas.py")
    else:
        print("❌ Some tests failed. Please check your API keys and setup.")
        print("\nRequired API keys:")
        print("- GOOGLE_API_KEY: https://makersuite.google.com/app/apikey")
        print("- OPENAI_API_KEY: https://platform.openai.com/api-keys")

if __name__ == "__main__":
    main() 