from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    csv_output_path: str = "./output/filtered_resumes.csv" # Output path for valid candidates
    use_openai: bool = False  # Feature flag to disable OpenAI integration
    openai_api_key: Optional[str] = None  # Optional: OpenAI API key for AI summary generation
    min_keyword_score: Optional[int] = 50  # Optional: Minimum keyword score threshold (default: 50)
    resume_folder_path: Optional[str] = None  # Optional: Path to folder containing resumes for Excel hyperlinks

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()




