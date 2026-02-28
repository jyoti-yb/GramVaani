import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class CropRetriever:
    def __init__(self):
        print("Loading FAISS index...")
        self.index = faiss.read_index(os.path.join(INDEX_DIR, "index.faiss"))

        print("Loading metadata...")
        with open(os.path.join(INDEX_DIR, "chunks_metadata.json"), "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        print("Loading embedding model...")
        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query, top_k=5):
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            results.append(self.metadata[idx])

        return results


if __name__ == "__main__":
    retriever = CropRetriever()

    query = input("Ask your farming question: ")
    results = retriever.search(query)

    print("\nTop Results:\n")
    for r in results:
        print(f"Crop: {r['crop']}")
        print(f"Section: {r['section']}")
        print(r["content"][:300])
        print("-" * 50)