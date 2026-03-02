import asyncio
from abc import ABC, abstractmethod
from typing import List

from openai import AsyncOpenAI
from openai import RateLimitError, APIConnectionError
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 1536

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"

    async def embed(self, text: str) -> List[float]:
        try:
            logger.info("Generating embedding", extra={"text_lenght": len(text)})

            response = await asyncio.wait_for(
                self.client.embeddings.create(
                    model=self.model,
                    input=text,
                ),
                timeout=10,
            )

            logger.info("Embedding generated successfully")

            return response.data[0].embedding
        
        except asyncio.TimeoutError:
            logger.error("Embedding timeout")
            raise

        except RateLimitError:
            logger.error("OpenAI rate limit hit")
            raise

        except APIConnectionError:
            logger.error("OpenAI connection error")
            raise

        except Exception as e:
            logger.exception("Unexpected embedding error")
            raise
        

embedding_provider: BaseEmbeddingProvider = OpenAIEmbeddingProvider()