from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    # LLM/API keys
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    xai_api_key: str = Field(default="", alias="XAI_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")

    # External services
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")

    # Storage/config
    database_url: str = Field(default="sqlite:////workspace/backend/data/app.db", alias="DATABASE_URL")
    chroma_dir: str = Field(default="/workspace/backend/storage/chroma", alias="CHROMA_DIR")

    # Models and endpoints
    llm_model_name: str = Field(default="x-ai/grok-3", alias="MODEL_NAME")
    xai_base_url: str = Field(default="https://api.x.ai/v1", alias="XAI_BASE_URL")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    model_config = {
        "protected_namespaces": ("settings_",),
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()