import json
import re
import ollama
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import pipeline


print("===== MediLens Medical AI =====")

# ==========================
# LOAD PUBMED TEXT CHUNKS
# ==========================

print("Loading PubMed texts...")

with open("medilens_rag/texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

print(f"Loaded {len(texts)} PubMed chunks")

# ==========================
# LOAD FAISS INDEX
# ==========================

print("Loading FAISS index...")

index = faiss.read_index("medilens_rag/pubmed_index.faiss")

print("FAISS index loaded\n")

# ==========================
# LOAD MODELS
# ==========================

print("Loading models...")

import torch
use_cuda = torch.cuda.is_available()
device = 0 if use_cuda else -1
print(f"Device: {'cuda' if use_cuda else 'cpu'}")

embedder = SentenceTransformer(
    "pritamdeka/PubMedBERT-mnli-snli-scinli-scitail-mednli-stsb",
    device='cuda' if use_cuda else 'cpu'
)

reranker = None
try:
    reranker = CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device='cuda' if use_cuda else 'cpu'
    )
except Exception as e:
    print(f"Could not load reranker (low resource fallback): {e}")

try:
    generator = pipeline(
        "text-generation",
        model="google/flan-t5-small",
        device=device,
        max_length=128,
        do_sample=False
    )
except Exception as e:
    print(f"Could not load generator model - using Bootstrapped fallback: {e}")
    generator = None

ner_candidates = [
    "pubmedbert_ner_model",
    "medlens_biobert",
    "d4data/biomedical-ner-all",
    "dslim/bert-base-NER"
]

ner_pipeline = None
for candidate in ner_candidates:
    try:
        ner_pipeline = pipeline(
            "ner",
            model=candidate,
            aggregation_strategy="simple",
            device=device
        )
        print(f"Loaded NER model: {candidate}")
        break
    except TypeError as e:
        print(f"NER pipeline arg mismatch for {candidate}: {e}; retrying without aggregation")
        try:
            ner_pipeline = pipeline(
                "ner",
                model=candidate,
                device=device
            )
            print(f"Loaded NER model (fallback): {candidate}")
            break
        except Exception as e2:
            print(f"Failed to load NER model {candidate} (fallback): {e2}")
    except Exception as e:
        print(f"Failed to load NER model {candidate}: {e}")

if ner_pipeline is None:
    raise RuntimeError("No NER model could be loaded; install one of the supported models.")

print("Models loaded\n")


# ==========================
# QUERY REWRITE
# ==========================

def rewrite_query(question):

    prompt = f"""
Convert the patient question into medical search keywords.

Return ONLY comma separated keywords.

Example:
eye pressure, orbital pain, proptosis

Patient question:
{question}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response["message"]["content"]

    text = re.sub(r"[\*\n]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================
# ENTITY EXTRACTION
# ==========================

def extract_entities(question):

    try:
        ner_results = ner_pipeline(question)

        entities = []

        for ent in ner_results:
            if ent["score"] > 0.6:
                entities.append(ent["word"])

        if len(entities) > 0:
            return entities

    except:
        pass

    tokens = re.findall(r"[a-zA-Z]+", question)

    stopwords = {
        "i","my","the","is","am","are",
        "a","an","this","that","why",
        "what","how","when"
    }

    return [t for t in tokens if t.lower() not in stopwords]


# ==========================
# RETRIEVAL
# ==========================

def retrieve_documents(query, top_k=5):

    q_embedding = embedder.encode([query])

    distances, indices = index.search(
        np.array(q_embedding),
        top_k
    )

    docs = []

    for idx in indices[0]:
        docs.append(texts[idx])

    return docs, indices[0]


# ==========================
# RERANK
# ==========================

def rerank_documents(query, docs):
    if reranker is None:
        return docs

    pairs = [(query, d) for d in docs]

    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    ranked_docs = [r[0] for r in ranked]

    return ranked_docs


# ==========================
# BUILD CONTEXT
# ==========================

def build_context(docs):

    trimmed = []

    for doc in docs[:3]:
        trimmed.append(doc[:400])

    return "\n".join(trimmed)


# ==========================
# BIOGPT GENERATION
# ==========================

def generate_medical_answer(question, context):

    prompt = f"""
Patient question:
{question}

Medical research context:
{context}

Explain possible medical causes clearly.
"""

    if generator is None:
        return "Could not generate an AI response due to missing model. Please consult a healthcare professional and verify your environment."

    try:
        result = generator(
            prompt,
            max_new_tokens=200,
            truncation=True
        )
        return result[0].get("generated_text", "")
    except Exception as e:
        print(f"Generator error: {e}")
        return "Could not generate medical explanation right now. Please consult a healthcare professional."


# ==========================
# SIMPLIFY ANSWER
# ==========================

def simplify_answer(answer):

    prompt = f"""
Rewrite this medical explanation in simple language
for a patient.

{answer}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


# ==========================
# MAIN LOOP
# ==========================

while True:

    question = input("\nAsk a medical question (or type 'exit'): ")

    if question.lower() == "exit":
        break

    print("\nRewriting query using medical knowledge...")

    medical_query = rewrite_query(question)

    print("Medical Query:", medical_query)

    print("\nExtracting medical entities...")

    entities = extract_entities(question)

    print("Entities:", entities)

    print("\nRetrieving medical knowledge...")

    retrieved_docs, doc_ids = retrieve_documents(medical_query)

    reranked_docs = rerank_documents(
        medical_query,
        retrieved_docs
    )

    context = build_context(reranked_docs)

    print("\nGenerating medical explanation...")

    answer = generate_medical_answer(
        question,
        context
    )

    final_answer = simplify_answer(answer)

    print("\n--- MediLens Response ---\n")

    print(final_answer)

    print("\n--- Research References Used ---\n")

    for i, idx in enumerate(doc_ids[:3]):

        print(f"Paper {i+1}:")
        print(texts[idx][:300])
        print()