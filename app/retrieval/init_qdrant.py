from app.retrieval.vector_client import create_semantic_memory_collection

if __name__ == "__main__":
    create_semantic_memory_collection()
    print("Qdrant semantic memory collection created.")