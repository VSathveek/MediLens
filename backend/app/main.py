import logging

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import get_settings
from .ocr import extract_text
from .pipeline import process_question
from .rag import get_rag_store
from .schemas import HealthResponse, ProcessRequest, ProcessResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medilens.main")

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="MediLens API", version="2.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def warm_rag_store():
    get_rag_store()


@app.get("/api/health", response_model=HealthResponse)
def health():
    store = get_rag_store()
    return HealthResponse(
        status="ok",
        gen_model=settings.gen_model,
        rag_chunks=store.size,
    )


@app.post("/api/process", response_model=ProcessResponse)
@limiter.limit("15/minute")
def process(request: Request, body: ProcessRequest):
    question = (body.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")

    try:
        return process_question(question, body.system_prompt)
    except Exception as e:
        logger.exception("process_question failed")
        raise HTTPException(status_code=502, detail=f"Failed to process request: {e}") from e


@app.post("/api/upload", response_model=ProcessResponse)
@limiter.limit("5/minute")
async def upload(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        raw_text = extract_text(contents)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Could not read any text from the image")

    try:
        return process_question(raw_text, None)
    except Exception as e:
        logger.exception("process_question failed for upload")
        raise HTTPException(status_code=502, detail=f"Failed to process request: {e}") from e


@app.get("/")
def root():
    return {
        "app": "MediLens",
        "version": "2.0.0",
        "endpoints": {
            "health": "GET /api/health",
            "process": "POST /api/process",
            "upload": "POST /api/upload",
        },
    }
