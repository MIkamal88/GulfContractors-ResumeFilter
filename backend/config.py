from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Feature flag to disable AI integration
    use_ai: bool = os.getenv("USE_AI", "True").lower() in ("true", "1", "yes")

    # AI provider chain. Primary is tried first; fallbacks (comma-separated)
    # are tried in order on transient failures. Providers without an API key
    # are silently skipped, so deployments can opt in to as many as they want.
    ai_provider_primary: str = os.getenv("AI_PROVIDER_PRIMARY", "gemini")
    ai_provider_fallbacks: str = os.getenv("AI_PROVIDER_FALLBACKS", "groq,openrouter")

    # Gemini (Google AI Studio) https://aistudio.google.com/apikey
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    # Groq (https://console.groq.com/keys) - free tier
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # OpenRouter (https://openrouter.ai/keys) - 50 RPD free, 1000 RPD with credits
    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    openrouter_model: str = os.getenv(
        "OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"
    )
    openrouter_fallback_model: str = os.getenv(
        "OPENROUTER_FALLBACK_MODEL", "minimax/minimax-m2.7:free"
    )
    openrouter_site_url: str = os.getenv("OPENROUTER_SITE_URL", "")
    openrouter_app_name: str = os.getenv(
        "OPENROUTER_APP_NAME", "GulfContractors-ResumeFilter"
    )

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
