# MediLens — Medical AI Assistant

An AI-powered medical assistant: patients describe symptoms or upload a
prescription photo, and MediLens explains likely causes, extracts entities,
and grounds its answer in PubMed research excerpts.

**Educational tool only — not a substitute for professional medical advice.**

## Architecture

```
my-app/    React + Vite frontend            -> deployed to Vercel
backend/   FastAPI backend                  -> deployed to Render (Docker)
scripts/   Offline data-prep (RAG corpus)   -> run locally, not deployed
```

The backend is a single FastAPI service (no local ML models, no GPU needed):

1. **Triage + rewrite + NER** — one Gemini call classifies whether the
   question is in-scope, rewrites it into PubMed-style search keywords, and
   extracts symptoms/medications/conditions/body parts as structured JSON.
2. **Retrieval** — the rewritten query is matched against a ~20,000-chunk
   PubMed corpus using a local TF-IDF index (`backend/data/`). This runs
   entirely in-process — no embedding API call, no rate-limit risk.
3. **Answer generation** — a second Gemini call writes a patient-friendly
   explanation grounded in the top retrieved excerpts.

Why TF-IDF instead of embeddings: the Gemini free-tier embedding quota is
too tight to reliably power live per-query retrieval (it's exhausted after
a handful of requests). TF-IDF is computed locally with scikit-learn, has
no external dependency at request time, fits comfortably in a free-tier
512MB instance, and is a strong baseline for keyword-heavy biomedical text.
Gemini is used only for the two generation calls per query.

Prescription image OCR uses `pytesseract` (the `tesseract-ocr` binary is
installed via the backend Dockerfile).

### Research artifacts

The original fine-tuned models (`medlens_biobert/`, `pubmedbert_ner_model/`,
`biogpt_model/`), the full 262k-chunk PubMed dump (`medilens_rag/`), and the
evaluation script (`model_performance_test.py`) are kept locally for
reproducing the paper's results, but are **not** used by the deployed app —
they're excluded from git via `.gitignore` since they're multiple GB. The
production RAG corpus is a trimmed, resampled subset built by
`scripts/build_rag_corpus.py`.

## Local development

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # fill in GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com/apikey).

### Frontend

```bash
cd my-app
npm install
cp .env.example .env.local    # VITE_BACKEND_URL=http://localhost:8000
npm run dev
```

Open http://localhost:5173.

### Rebuilding the RAG corpus

Only needed if you want a different corpus size or fresh data:

```bash
python scripts/build_rag_corpus.py --target 20000
```

Writes `backend/data/rag_vectorizer.pkl`, `rag_matrix.npz`, `rag_corpus.json`
(~35MB total — commit directly, no Git LFS needed).

## Deployment

### Backend → Render

1. Push this repo to GitHub.
2. In Render: **New → Blueprint**, point it at the repo (uses `render.yaml`
   at the repo root), or manually create a **Web Service** with:
   - Runtime: Docker
   - Dockerfile path: `backend/Dockerfile`
   - Docker context: `backend`
   - Plan: Free
3. Set the `GEMINI_API_KEY` environment variable in the Render dashboard
   (never commit it).
4. Set `CORS_ORIGINS` to your Vercel domain once you have it (comma-separate
   multiple origins).
5. Health check path: `/api/health`.

### Frontend → Vercel

1. In Vercel: **New Project**, import the repo, set **Root Directory** to
   `my-app`.
2. Framework preset: Vite (auto-detected via `my-app/vercel.json`).
3. Set the environment variable `VITE_BACKEND_URL` to your Render backend
   URL (e.g. `https://medilens-backend.onrender.com`).
4. Deploy. Update the backend's `CORS_ORIGINS` with the resulting Vercel
   domain.

### Notes on the free tiers

- Render's free plan spins the service down after inactivity — the first
  request after idling will be slow (cold start) while the container boots
  and loads the ~35MB TF-IDF corpus into memory.
- Gemini's free tier has request-rate limits; the backend applies its own
  per-IP rate limiting (`15/min` on `/api/process`, `5/min` on
  `/api/upload`) to avoid burning through the daily quota from abuse.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check + loaded corpus size |
| `/api/process` | POST | `{ question, system_prompt? }` → full pipeline |
| `/api/upload` | POST | multipart `file` (prescription image) → OCR + pipeline |

```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"question": "I have a persistent cough and mild fever for three days"}'
```

## Disclaimer

MediLens is an AI-powered educational tool only. It is **not** a substitute
for professional medical advice — always consult a qualified healthcare
provider.
