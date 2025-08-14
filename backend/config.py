from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    # LLM/API keys
    github_models_api_key: str = Field(default="", alias="GITHUB_MODELS_API_KEY")

    # External services
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")

    # Storage/config
    database_url: str = Field(default="sqlite:////workspace/backend/data/app.db", alias="DATABASE_URL")
    chroma_dir: str = Field(default="/workspace/backend/storage/chroma", alias="CHROMA_DIR")

    # Models and endpoints
    llm_model_name: str = Field(default="openai/gpt-4o", alias="MODEL_NAME")
    github_models_base_url: str = Field(default="", alias="GITHUB_MODELS_BASE_URL")
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