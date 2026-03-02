from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str
    qdrant_url: str
    openai_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()