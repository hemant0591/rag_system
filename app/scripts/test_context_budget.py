from app.llm.tokenizer import TokenCounter
from app.llm.context_budget import ContextBudget
from app.core.config import settings

counter = TokenCounter(settings.generation_model)

available = (
    settings.max_model_tokens
    - settings.reserved_output_tokens
    - settings.safety_buffer_tokens
)

budget = ContextBudget(counter, available)

print("Can add short text:", budget.can_add_text("hello world"))
print("Remaining:", budget.remaining_tokens)