import gzip
import xml.etree.ElementTree as ET
import json
import os

INPUT_DIR = "pubmed_xml"
OUTPUT = "pubmed_dataset.jsonl"

with open(OUTPUT, "w", encoding="utf-8") as out:

    for file in os.listdir(INPUT_DIR):

        if not file.endswith(".gz"):
            continue

        print("Processing:", file)

        with gzip.open(os.path.join(INPUT_DIR, file), "rb") as f:

            tree = ET.parse(f)
            root = tree.getroot()

            for article in root.findall(".//PubmedArticle"):

                try:
                    title = article.findtext(".//ArticleTitle")

                    abstract_parts = article.findall(".//AbstractText")
                    abstract = " ".join(
                        [a.text for a in abstract_parts if a.text]
                    )

                    if not abstract:
                        continue

                    record = {
                        "text": title + " " + abstract
                    }

                    out.write(json.dumps(record) + "\n")

                except:
                    pass