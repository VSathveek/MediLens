from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str
    gen_model: str = "gemini-2.5-flash"

    rag_data_dir: Path = BASE_DIR / "data"
    rag_top_k: int = 5
    rag_context_docs: int = 3
    rag_context_chars: int = 500

    cors_origins: str = "http://localhost:5173"

    max_question_length: int = 2000
    max_upload_bytes: int = 8 * 1024 * 1024  # 8MB

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def rag_vectorizer_path(self) -> Path:
        return self.rag_data_dir / "rag_vectorizer.pkl"

    @property
    def rag_matrix_path(self) -> Path:
        return self.rag_data_dir / "rag_matrix.npz"

    @property
    def rag_corpus_path(self) -> Path:
        return self.rag_data_dir / "rag_corpus.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
