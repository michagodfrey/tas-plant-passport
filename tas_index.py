# tas_index.py
# This file creates a searchable index of the Tasmanian Plant Quarantine Manual (PQM)
# It uses OpenAI embeddings to convert text into vectors that can be semantically searched
# Note: We use OpenAI embeddings because Gemini doesn't provide embedding capabilities

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import re
from langchain_core.documents import Document

# Load environment variables (including OPENAI_API_KEY for embeddings)
load_dotenv()

# Path to the local PDF file
PDF_PATH = "pdfs/tas_pqm.pdf"

try:
    # Load the PDF document from the local file
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    # Create a text splitter to break the document into smaller chunks
    # This is necessary because:
    # 1. Language models have token limits
    # 2. Smaller chunks allow for more precise retrieval
    # 3. Overlapping chunks help maintain context
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,        # Maximum size of each text chunk
        chunk_overlap=200,     # Number of characters to overlap between chunks
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],  # Split on these characters in order
        length_function=len,   # Function to measure chunk size
        is_separator_regex=False  # Don't treat separators as regex patterns
    )

    # Process each document and add metadata
    chunks = []
    for doc in docs:
        # Try to extract section information from the text
        # This helps with providing context in search results
        section_info = ""
        if "Section" in doc.page_content:
            section_match = re.search(r"Section\s+(\d+[\.\d]*)", doc.page_content)
            if section_match:
                section_info = section_match.group(0)
        
        # Split the document into chunks
        doc_chunks = splitter.split_text(doc.page_content)
        
        # Add metadata to each chunk
        # This helps with:
        # 1. Tracking which page the information came from
        # 2. Maintaining source information
        # 3. Preserving section context
        for chunk in doc_chunks:
            chunks.append(Document(
                page_content=chunk,
                metadata={
                    "page": doc.metadata.get("page", 0),
                    "source": "Tasmanian PQM 2024",
                    "section": section_info
                }
            ))

    # Create embeddings using OpenAI's embedding model
    # Note: We use OpenAI embeddings because Gemini doesn't provide embedding capabilities
    # This is a hybrid approach: OpenAI for embeddings, Gemini for text generation
    embeddings = OpenAIEmbeddings()

    # Create a vector store using FAISS (Facebook AI Similarity Search)
    # FAISS is an efficient library for similarity search and clustering of dense vectors
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Save the vector store to disk for later use
    vectorstore.save_local("tas_faiss_index")

    # Reload the vector store and create a retriever
    # This allows other modules to import and use the retriever
    vectorstore = FAISS.load_local("tas_faiss_index", embeddings,
                                   allow_dangerous_deserialization=True)

    # Create a retriever with specific search parameters
    retriever_tas = vectorstore.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance
        search_kwargs={
            "k": 5,         # Number of documents to retrieve
            "fetch_k": 10,  # Number of documents to fetch before selecting top k
            "lambda_mult": 0.7  # Balance between relevance and diversity
        }
    )

    print("[tas_index] retriever_tas ready.")

except Exception as e:
    print(f"An error occurred: {e}")
