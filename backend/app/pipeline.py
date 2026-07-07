"""Orchestrates the full request flow: triage -> retrieve -> answer."""

import logging

from . import gemini_client
from .config import get_settings
from .rag import get_rag_store
from .schemas import ProcessResponse, Reference

logger = logging.getLogger("medilens.pipeline")

OUT_OF_SCOPE_MESSAGE = (
    "I'm a dedicated medical assistant. Please ask a health-related question about "
    "symptoms, conditions, medications, treatments, or healthcare guidance."
)


def _flatten_entities(triage) -> list[str]:
    seen = []
    for group in (triage.symptoms, triage.medications, triage.conditions, triage.body_parts):
        for e in group:
            if e not in seen:
                seen.append(e)
    return seen


def process_question(question: str, system_prompt: str | None) -> ProcessResponse:
    settings = get_settings()
    question = question.strip()[: settings.max_question_length]

    triage = gemini_client.triage_and_rewrite(question)

    if not triage.in_scope:
        return ProcessResponse(
            question=question,
            medical_query="",
            entities=[],
            answer=OUT_OF_SCOPE_MESSAGE,
            references=[],
        )

    rag_store = get_rag_store()
    hits = rag_store.search(triage.rewritten_query or question, top_k=settings.rag_top_k)
    top_hits = hits[: settings.rag_context_docs]

    context = "\n".join(h.text[: settings.rag_context_chars] for h in top_hits)
    answer = gemini_client.generate_answer(question, context, system_prompt)

    references = [
        Reference(paper=i + 1, text=h.text[: settings.rag_context_chars], score=round(h.score, 3))
        for i, h in enumerate(top_hits)
    ]

    return ProcessResponse(
        question=question,
        medical_query=triage.rewritten_query,
        entities=_flatten_entities(triage),
        answer=answer,
        references=references,
    )
