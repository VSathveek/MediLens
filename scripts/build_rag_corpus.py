"""
Build a small, production-sized RAG corpus for MediLens.

Takes the existing 262k-chunk PubMed dump (medilens_rag/texts.json), filters
and samples it down to a target size, and fits a TF-IDF index over it.

Why TF-IDF instead of embeddings: the Gemini API's free-tier embedding quota
is tight enough that it can't reliably power either a one-time corpus build
or, more importantly, live per-query embedding calls in production. TF-IDF
is computed entirely locally (scikit-learn), has zero API/rate-limit
dependency, fits easily in a 512MB instance, and is a strong baseline for
keyword-heavy biomedical retrieval. Gemini is reserved for the generation
calls in the pipeline (triage/rewrite + final answer).

Output (small enough to commit directly to git, no LFS needed):
    backend/data/rag_vectorizer.pkl  -- fitted TfidfVectorizer
    backend/data/rag_matrix.npz      -- sparse TF-IDF matrix (one row per chunk)
    backend/data/rag_corpus.json     -- chunk texts, same row order as the matrix

Usage:
    python scripts/build_rag_corpus.py --target 20000
"""

import argparse
import json
import pickle
import random
from pathlib import Path

from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent.parent
SOURCE_TEXTS = ROOT / "medilens_rag" / "texts.json"
OUT_DIR = ROOT / "backend" / "data"
VECTORIZER_OUT = OUT_DIR / "rag_vectorizer.pkl"
MATRIX_OUT = OUT_DIR / "rag_matrix.npz"
CORPUS_OUT = OUT_DIR / "rag_corpus.json"

MIN_CHARS = 150
MAX_CHARS = 2200
SEED = 42


def select_chunks(target: int) -> list[str]:
    with open(SOURCE_TEXTS, encoding="utf-8") as f:
        texts = json.load(f)

    seen = set()
    candidates = []
    for t in texts:
        t = t.strip()
        if not (MIN_CHARS <= len(t) <= MAX_CHARS):
            continue
        if t in seen:
            continue
        seen.add(t)
        candidates.append(t)

    random.Random(SEED).shuffle(candidates)
    return candidates[:target]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=20000)
    parser.add_argument("--max-features", type=int, default=60000)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Selecting {args.target} chunks from {SOURCE_TEXTS} ...")
    chunks = select_chunks(args.target)
    print(f"Selected {len(chunks)} chunks (min={MIN_CHARS}, max={MAX_CHARS} chars)")

    print("Fitting TF-IDF vectorizer ...")
    vectorizer = TfidfVectorizer(
        max_features=args.max_features,
        ngram_range=(1, 2),
        stop_words="english",
        sublinear_tf=True,
        min_df=2,
    )
    matrix = vectorizer.fit_transform(chunks)
    print(f"Matrix shape: {matrix.shape}, vocabulary size: {len(vectorizer.vocabulary_)}")

    with open(VECTORIZER_OUT, "wb") as f:
        pickle.dump(vectorizer, f)
    sparse.save_npz(MATRIX_OUT, matrix)
    with open(CORPUS_OUT, "w", encoding="utf-8") as f:
        json.dump(chunks, f)

    print(f"Wrote {VECTORIZER_OUT} ({VECTORIZER_OUT.stat().st_size / 1e6:.1f} MB)")
    print(f"Wrote {MATRIX_OUT} ({MATRIX_OUT.stat().st_size / 1e6:.1f} MB)")
    print(f"Wrote {CORPUS_OUT} ({CORPUS_OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
