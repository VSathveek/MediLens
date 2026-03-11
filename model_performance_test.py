import requests
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# CONFIG
# -----------------------------

API = "http://localhost:5001/api/process"

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# TEST DATASET
# -----------------------------

tests = [

{
"question":"I have persistent cough and fever what could this mean",
"reference":"Persistent cough and fever may indicate respiratory infection such as bronchitis or pneumonia."
},

{
"question":"Sudden severe headache and dizziness",
"reference":"Severe headache and dizziness may indicate migraine stroke or hypertension."
},

{
"question":"What are symptoms of diabetes",
"reference":"Common diabetes symptoms include frequent urination excessive thirst fatigue and blurred vision."
}

]

# -----------------------------
# SOTA BENCHMARK SCORES
# -----------------------------

SOTA = {

"BioGPT":{
"rouge":0.32,
"semantic":0.78
},

"PubMedGPT":{
"rouge":0.35,
"semantic":0.81
},

"ClinicalBERT":{
"rouge":0.29,
"semantic":0.74
}

}

# -----------------------------
# METRICS
# -----------------------------

def rouge_l(reference,prediction):

    scorer = rouge_scorer.RougeScorer(
        ["rougeL"],
        use_stemmer=True
    )

    score = scorer.score(reference,prediction)

    return score["rougeL"].fmeasure


def semantic(reference,prediction):

    e1 = embedder.encode([reference])
    e2 = embedder.encode([prediction])

    return cosine_similarity(e1,e2)[0][0]


# -----------------------------
# QUERY MEDILENS
# -----------------------------

def query(question):

    start=time.time()

    r=requests.post(API,json={"question":question})

    latency=time.time()-start

    data=r.json()

    return data["answer"],latency


# -----------------------------
# RUN EVALUATION
# -----------------------------

rouge_scores=[]
semantic_scores=[]
latencies=[]

for t in tests:

    print("Testing:",t["question"])

    ans,lat=query(t["question"])

    r=rouge_l(t["reference"],ans)
    s=semantic(t["reference"],ans)

    rouge_scores.append(r)
    semantic_scores.append(s)
    latencies.append(lat)

# Average MediLens scores

medilens_rouge=np.mean(rouge_scores)
medilens_semantic=np.mean(semantic_scores)
medilens_latency=np.mean(latencies)

print("\nMediLens Scores")
print("ROUGE-L:",medilens_rouge)
print("Semantic:",medilens_semantic)
print("Latency:",medilens_latency)

# -----------------------------
# BUILD COMPARISON TABLE
# -----------------------------

models=["MediLens"]+list(SOTA.keys())

rouge_values=[medilens_rouge]
semantic_values=[medilens_semantic]

for m in SOTA:

    rouge_values.append(SOTA[m]["rouge"])
    semantic_values.append(SOTA[m]["semantic"])

# -----------------------------
# PLOTS
# -----------------------------

sns.set_style("whitegrid")

# ROUGE comparison

plt.figure()

plt.bar(models,rouge_values)

plt.title("ROUGE-L Comparison (MediLens vs SOTA)")
plt.ylabel("ROUGE-L")

plt.show()


# Semantic similarity comparison

plt.figure()

plt.bar(models,semantic_values)

plt.title("Semantic Similarity Comparison")
plt.ylabel("Score")

plt.show()


# Latency (only MediLens measured)

plt.figure()

plt.bar(["MediLens"],[medilens_latency])

plt.title("Average System Latency")

plt.ylabel("Seconds")

plt.show()