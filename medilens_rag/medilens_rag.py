import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("pritamdeka/PubMedBERT-mnli-snli-scinli-scitail-mednli-stsb")

index = faiss.read_index("pubmed_index.faiss")

texts = json.load(open("texts.json"))

def search(query):

    query_vec = model.encode([query])

    D, I = index.search(np.array(query_vec), 5)

    results = [texts[i] for i in I[0]]

    return results


while True:

    q = input("\nAsk MediLens: ")

    results = search(q)

    print("\nTop medical evidence:\n")

    for r in results:
        print("-", r[:300], "\n")