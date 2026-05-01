from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Feature flag to disable AI integration
    use_ai: bool = os.getenv("USE_AI", "True").lower() in ("true", "1", "yes")
    # Gemini API key for AI summary generation
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    # Gemini model to use
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # Minimum keyword score threshold (default: 50)
    min_keyword_score: int = int(os.getenv("MIN_KEYWORD_SCORE", "50"))

    # CORS allowed origins (comma-separated or *)
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")

    # Storage file for custom job profiles
    storage_json: str = os.getenv("STORAGE_JSON", "data/custom_profiles.json")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
