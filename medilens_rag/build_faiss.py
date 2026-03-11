import faiss
import numpy as np
import json

embeddings = np.load("embeddings.npy")

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

faiss.write_index(index, "pubmed_index.faiss")

print("Index built with", index.ntotal, "vectors")