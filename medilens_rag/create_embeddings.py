import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("pritamdeka/PubMedBERT-mnli-snli-scinli-scitail-mednli-stsb")

texts = []

with open("pubmed_chunks.jsonl") as f:
    for line in f:
        texts.append(json.loads(line)["text"])

print("Creating embeddings...")

embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

np.save("embeddings.npy", embeddings)

with open("texts.json", "w") as f:
    json.dump(texts, f)