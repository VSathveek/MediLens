import json

INPUT = "pubmed_dataset.jsonl"
OUTPUT = "pubmed_chunks.jsonl"

CHUNK_SIZE = 500

def chunk_text(text):

    words = text.split()

    for i in range(0, len(words), CHUNK_SIZE):
        yield " ".join(words[i:i+CHUNK_SIZE])


with open(INPUT) as f, open(OUTPUT, "w") as out:

    for line in f:

        data = json.loads(line)

        for chunk in chunk_text(data["text"]):

            out.write(json.dumps({"text": chunk}) + "\n")