from pathlib import Path


def load_system_prompt() -> str:
    path = Path(__file__).parent / "system_prompt.txt"
    return path.read_text().strip()