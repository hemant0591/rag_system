from typing import List, Dict

from app.llm.context_budget import ContextBudget

class ContextAssembler:
    def __init__(self, budget: ContextBudget):
        self.budget = budget
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str) -> bool:
        if self.budget.can_add_text(content):
            self.budget.add_text(content)
            self.messages.append({"role": role, "content": content})
            return True
        return False
    
    def build(self) -> List[Dict[str, str]]:
        return self.messages

    @property 
    def used_tokens(self) -> int:
        return self.budget.used_tokens