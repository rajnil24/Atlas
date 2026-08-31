import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str

    database_url: str
    redis_url: str

    groq_api_key: str

    open_weather_api_key : str

    tavily_api_key:str

    gemini_api_key:str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

settings.postgres_user = os.getenv('POSTGRES_USER')
settings.postgres_password = os.getenv('POSTGRES_PASSWORD')
settings.postgres_db = os.getenv('POSTGRES_DB')
settings.database_url = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@localhost:5432/{settings.postgres_db}"
)
load_dotenv()
settings.groq_api_key = os.getenv("GROQ_API_KEY")
settings.open_weather_api_key = os.getenv("OPEN_WEATHER_API_KEY")
settings.tavily_api_key = os.getenv("TAVILY_API_KEY")
settings.gemini_api_key = os.getenv("GEMINI_API_KEY")
