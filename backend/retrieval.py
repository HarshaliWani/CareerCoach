from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import get_settings


class VectorStoreSingleton:
    _instance: Chroma | None = None

    @classmethod
    def get_store(cls) -> Chroma:
        if cls._instance is not None:
            return cls._instance
        settings = get_settings()
        Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        cls._instance = Chroma(persist_directory=settings.chroma_dir, embedding_function=embeddings)
        return cls._instance


def retrieve_relevant(query: str, k: int = 5) -> List[Document]:
    store = VectorStoreSingleton.get_store()
    try:
        docs = store.similarity_search(query, k=k)
    except Exception:
        docs = []
    return docs