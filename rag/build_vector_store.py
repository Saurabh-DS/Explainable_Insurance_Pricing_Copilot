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
    
    # Load guidelines
    ids = []
    documents = []
    metadatas = []
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            path = os.path.join(data_dir, filename)
            with open(path, "r") as f:
                content = f.read()
                
            ids.append(filename)
            documents.append(content)
            metadatas.append({"source": filename})
    
    # Upsert to collection
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Indexed {len(documents)} guideline documents into ChromaDB at {persist_directory}")

if __name__ == "__main__":
    build_vector_store()
