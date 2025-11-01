from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Output path for valid candidates
    csv_output_path: str = os.getenv("CSV_OUTPUT_PATH", "/app/output/filtered_resumes.csv")
    
    # Feature flag to disable OpenAI integration
    use_openai: bool = os.getenv("USE_OPENAI", "True").lower() in ("true", "1", "yes")
    
    # OpenAI API key for AI summary generation
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Minimum keyword score threshold (default: 50)
    min_keyword_score: int = int(os.getenv("MIN_KEYWORD_SCORE", "50"))
    
    # Path to folder containing resumes for Excel hyperlinks
    resume_folder_path: Optional[str] = os.getenv("RESUME_FOLDER_PATH", "/app/resumes")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()




