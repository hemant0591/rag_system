import tiktoken
from functools import lru_cache

class TokenCounter:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.encoding = self._get_encoding(model_name)

    @staticmethod
    @lru_cache(maxsize=10)
    def _get_encoding(model_name: str):
        return tiktoken.encoding_for_model(model_name)
    
    def count_text(self, text: str):
        return len(self.encoding.encode(text))
    
    def count_messages(self, messages: list[dict]) -> int:
        """
        messages format:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
        ]
        """
        total = 0
        for msg in messages:
            total += self.count_text(msg["role"])
            total += self.count_text(msg["context"])

        return total