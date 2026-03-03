from abc import ABC, abstractmethod
from typing import List, Dict

import asyncio
import logging
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 500,
    ) -> str:
        pass


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.generation_model

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 500
    ) -> str:
        try:
            logger.info("Generating LLM response")

            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ),
                timeout=20,
            )

            logger.info("LLM response generated")

            return response.choices[0].message.content
        
        except asyncio.TimeoutError:
            logger.error("LLM generation timeout")
            raise

        except Exception:
            logger.exception("LLM generation failed")
            raise


llm_provider: BaseLLMProvider = OpenAILLMProvider()