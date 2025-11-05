from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Feature flag to disable OpenAI integration
    use_openai: bool = os.getenv("USE_OPENAI", "True").lower() in ("true", "1", "yes")
    
    # OpenAI API key for AI summary generation
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Minimum keyword score threshold (default: 50)
    min_keyword_score: int = int(os.getenv("MIN_KEYWORD_SCORE", "50"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()




