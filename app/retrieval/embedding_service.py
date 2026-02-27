import random

EMBEDDING_DIM = 1536

class EmbeddingService:
    def embed(self, text: str) -> list[float]:
        return [random.random() for _ in range(EMBEDDING_DIM)]
    
embedding_service = EmbeddingService()