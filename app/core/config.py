from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str
    qdrant_url: str
    openai_api_key: str
    generation_model: str = "gpt-4o-mini"
    max_model_tokens: int = 16000
    reserved_output_tokens: int = 1000
    safety_buffer_tokens: int = 500
    generation_safety_margin: int = 100

    class Config:
        env_file = ".env"

settings = Settings()