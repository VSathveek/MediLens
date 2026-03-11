import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm

BASE_URL = "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/"
SAVE_DIR = "pubmed_xml"

os.makedirs(SAVE_DIR, exist_ok=True)

print("Fetching file list...")

page = requests.get(BASE_URL).text
soup = BeautifulSoup(page, "html.parser")

files = [a.get("href") for a in soup.find_all("a") if a.get("href").endswith(".gz")]

for file in files[:20]:  # download first 20 files (~600k papers)

    url = BASE_URL + file
    path = os.path.join(SAVE_DIR, file)

    print("Downloading:", file)

    r = requests.get(url, stream=True)

    with open(path, "wb") as f:
        for chunk in tqdm(r.iter_content(chunk_size=8192)):
            f.write(chunk)