"""TF-IDF retrieval over the pre-built, trimmed PubMed corpus.

The vectorizer, sparse matrix, and corpus texts are all small (tens of MB)
and loaded once into memory at process startup -- see
scripts/build_rag_corpus.py. No external API calls are needed at query time,
which matters because the Gemini free-tier embedding quota is far too tight
to power live per-query retrieval.
"""

import json
import logging
import pickle
from dataclasses import dataclass

from scipy import sparse

from .config import get_settings

logger = logging.getLogger("medilens.rag")


@dataclass
class RagHit:
    text: str
    score: float


class RagStore:
    def __init__(self):
        settings = get_settings()
        self._vectorizer = None
        self._matrix = None
        self._corpus: list[str] = []

        paths = (settings.rag_vectorizer_path, settings.rag_matrix_path, settings.rag_corpus_path)
        if all(p.exists() for p in paths):
            with open(settings.rag_vectorizer_path, "rb") as f:
                self._vectorizer = pickle.load(f)
            self._matrix = sparse.load_npz(settings.rag_matrix_path)
            with open(settings.rag_corpus_path, encoding="utf-8") as f:
                self._corpus = json.load(f)
            logger.info("Loaded RAG corpus: %d chunks", len(self._corpus))
        else:
            logger.warning("RAG corpus files not found under %s -- retrieval disabled", settings.rag_data_dir)

    @property
    def ready(self) -> bool:
        return self._matrix is not None

    @property
    def size(self) -> int:
        return self._matrix.shape[0] if self.ready else 0

    def search(self, query: str, top_k: int) -> list[RagHit]:
        if not self.ready:
            return []

        query_vec = self._vectorizer.transform([query])
        scores = (self._matrix @ query_vec.T).toarray().ravel()
        if not scores.any():
            return []

        top_indices = scores.argsort()[::-1][:top_k]
        return [RagHit(text=self._corpus[i], score=float(scores[i])) for i in top_indices if scores[i] > 0]


_store: RagStore | None = None


def get_rag_store() -> RagStore:
    global _store
    if _store is None:
        _store = RagStore()
    return _store
