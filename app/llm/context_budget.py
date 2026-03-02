from app.llm.tokenizer import TokenCounter

class ContextBudget:
    def __init__(
            self,
            token_counter: TokenCounter,
            max_input_tokens: int,
    ):
        self.token_counter = token_counter
        self.max_input_tokens = max_input_tokens
        self.used_tokens = 0

    @property
    def remaining_tokens(self) -> int:
        return self.max_input_tokens - self.used_tokens
    
    def can_add_text(self, text: str) -> bool:
        tokens = self.token_counter.count_text(text)
        return tokens <= self.remaining_tokens 
    
    def add_text(self, text: str) -> bool:
        tokens = self.token_counter.count_text(text)

        if tokens > self.remaining_tokens:
            return False
        
        self.used_tokens += tokens
        return True
    
    def can_add_tokens(self, token_count: int) -> bool:
        return token_count <= self.remaining_tokens
    
    def add_tokens(self, token_count: int) -> bool:
        if token_count > self.remaining_tokens:
            return False
        
        self.used_tokens += token_count
        return True