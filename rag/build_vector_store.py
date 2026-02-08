import os
import chromadb
from chromadb.utils import embedding_functions

def build_vector_store():
    data_dir = "data/guidelines"
    persist_directory = "database/chroma_db"
    
    # Initialize Chroma Client
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Use default embedding function
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="underwriting_guidelines",
        embedding_function=embedding_func
    )
    
    # Load guidelines with chunking
    ids = []
    documents = []
    metadatas = []
    
    # Simple recursive chunking function
    def chunk_text(text, chunk_size=500, overlap=50):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a natural break point (newline, period, space)
            # Look back from 'end'
            break_found = False
            for split_char in ["\n\n", "\n", ". ", " "]:
                split_idx = text.rfind(split_char, start, end)
                if split_idx != -1 and split_idx > start + chunk_size // 2: # Ensure chunk isn't too small
                    end = split_idx + len(split_char) # Include the split char
                    break_found = True
                    break
            
            chunks.append(text[start:end])
            start = end - overlap # Move efficient overlap
        return chunks

    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            path = os.path.join(data_dir, filename)
            with open(path, "r") as f:
                content = f.read()
            
            # Create chunks
            chunks = chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                ids.append(f"{filename}_{i}")
                documents.append(chunk)
                metadatas.append({"source": filename, "chunk_index": i})
    
    # Upsert to collection
    # Chroma handles batching, but let's be safe if it's huge (it's not)
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Indexed {len(documents)} chunks from guidelines into ChromaDB at {persist_directory}")

def build_baseline_vector_store():
    data_dir = "data/guidelines"
    persist_directory = "database/chroma_db"
    
    # Initialize Chroma Client
    client = chromadb.PersistentClient(path=persist_directory)
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    
    # Create distinct baseline collection
    collection = client.get_or_create_collection(
        name="underwriting_guidelines_baseline",
        embedding_function=embedding_func
    )
    
    ids = []
    documents = []
    metadatas = []
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            path = os.path.join(data_dir, filename)
            with open(path, "r") as f:
                content = f.read()
            
            # NAIVE: Index entire file as one document
            ids.append(filename)
            documents.append(content)
            metadatas.append({"source": filename, "type": "whole_doc"})
    
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Indexed {len(documents)} whole documents into Baseline Collection at {persist_directory}")

if __name__ == "__main__":
    build_vector_store()
    build_baseline_vector_store()
