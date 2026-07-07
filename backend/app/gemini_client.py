"""Thin wrapper around the Gemini API: one client instance, retry/backoff,
and the three calls the pipeline needs (triage+rewrite, embed, generate)."""

import logging
import time

from google import genai
from google.genai import types

from .config import get_settings
from .schemas import TriageResult

logger = logging.getLogger("medilens.gemini")

_settings = get_settings()
_client = genai.Client(api_key=_settings.gemini_api_key)

_RETRYABLE_ATTEMPTS = 4
_BASE_DELAY = 1.5


def _with_retry(fn, *args, **kwargs):
    delay = _BASE_DELAY
    for attempt in range(_RETRYABLE_ATTEMPTS):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt == _RETRYABLE_ATTEMPTS - 1:
                raise
            logger.warning("Gemini call failed (attempt %d): %s", attempt + 1, str(e)[:200])
            time.sleep(delay)
            delay *= 2


TRIAGE_PROMPT = """You are the intake filter for MediLens, a medical information assistant.

Given the patient's message below, respond with JSON only:
- in_scope: true if this is a health/medical question (symptoms, conditions, medications, \
treatments, anatomy, prescriptions, healthcare guidance). false for anything else \
(small talk, coding, general trivia, etc).
- rewritten_query: if in_scope, rewrite the message as a short list of medical search \
keywords suitable for a PubMed search (comma separated, no explanation). Empty string otherwise.
- symptoms, medications, conditions, body_parts: if in_scope, extract any mentioned medical \
entities into these lists (lowercase, no duplicates). Empty lists otherwise.

Patient message:
{question}
"""

ANSWER_PROMPT = """{system_prompt}

Patient question:
{question}

Relevant medical research excerpts (for grounding only, do not quote verbatim or cite jargon):
{context}

Write a clear, empathetic, patient-friendly explanation of possible causes and general \
guidance. Use short paragraphs or bullet points. Do not provide a definitive diagnosis; \
remind the patient to consult a healthcare professional for anything serious.
"""

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, empathetic medical assistant. Answer only medical questions and "
    "emphasize safety and consulting a healthcare provider."
)


def triage_and_rewrite(question: str) -> TriageResult:
    def call():
        resp = _client.models.generate_content(
            model=_settings.gen_model,
            contents=TRIAGE_PROMPT.format(question=question),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TriageResult,
                temperature=0.1,
            ),
        )
        return resp.parsed

    return _with_retry(call)


def generate_answer(question: str, context: str, system_prompt: str | None) -> str:
    prompt = ANSWER_PROMPT.format(
        system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        question=question,
        context=context or "(no additional research context retrieved)",
    )

    def call():
        resp = _client.models.generate_content(
            model=_settings.gen_model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4),
        )
        return resp.text or ""

    return _with_retry(call)
