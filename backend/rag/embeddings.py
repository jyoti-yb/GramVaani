import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNKS_FILE = os.path.join(BASE_DIR, "knowledge_base", "chunks.json")
INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)

    print("Loading chunks...")
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [
    f"Crop: {chunk['crop']}\nSection: {chunk['section']}\n{chunk['content']}"
    for chunk in chunks
]

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)

    embeddings = np.array(embeddings).astype("float32")

    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(INDEX_DIR, "index.faiss"))

    with open(os.path.join(INDEX_DIR, "chunks_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f)

    print("Index built successfully!")


if __name__ == "__main__":
    build_index()