from typing import List, Dict
import json

from app.llm.tokenizer import TokenCounter
from app.llm.context_budget import ContextBudget
from app.llm.context_assembler import ContextAssembler
from app.core.config import settings

def build_context(
        system_prompt: str,
        structured_memory: List[str],
        semantic_memory: List[str],
        conversation_summary: str | None,
        recent_messages: List[Dict[str, str]] | None,
        current_user_input: str,
):

    counter = TokenCounter(settings.generation_model)

    max_tokens = (
        settings.max_model_tokens
        - settings.reserved_output_tokens
        - settings.safety_buffer_tokens
    )

    budget = ContextBudget(counter, max_tokens)
    assembler = ContextAssembler(budget)

    # Add system prompt
    assembler.add_message(role="system", content=system_prompt)

    # Add structured memory
    if structured_memory:
        structured_block = {
            "user_preferences": structured_memory
        }
        assembler.add_message(
            "system",
            json.dumps(structured_block)
        )

    # Add semantic memory
    if semantic_memory:
        semantic_block = {
            "relevant_long_term_memory": semantic_memory
        }
        assembler.add_message(
            "system",
            json.dumps(semantic_block)
        )

    # Add conversation memory
    if conversation_summary:
        assembler.add_message("system", f"Conversation summary: {conversation_summary}")

    # Add recent messages
    if recent_messages:
        for msg in recent_messages:
            if not assembler.add_message(msg["role"], msg["content"]):
                break

    # Add user message
    assembler.add_message("user", current_user_input)
                          
    return assembler.build(), assembler.used_tokens
