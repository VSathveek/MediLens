from pydantic import BaseModel, Field


class TriageResult(BaseModel):
    """Structured output from the single triage+rewrite+NER Gemini call."""

    in_scope: bool
    rewritten_query: str = ""
    symptoms: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    body_parts: list[str] = Field(default_factory=list)


class Reference(BaseModel):
    paper: int
    text: str
    score: float


class ProcessRequest(BaseModel):
    question: str
    system_prompt: str | None = None


class ProcessResponse(BaseModel):
    question: str
    medical_query: str
    entities: list[str]
    answer: str
    references: list[Reference]


class HealthResponse(BaseModel):
    status: str
    gen_model: str
    rag_chunks: int
