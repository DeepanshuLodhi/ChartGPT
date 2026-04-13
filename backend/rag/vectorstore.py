import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rag.echarts_docs import get_docs

CACHE_DIR = os.path.dirname(__file__)
INDEX_FILE = os.path.join(CACHE_DIR, "faiss_index.pkl")
CHUNKS_FILE = os.path.join(CACHE_DIR, "chunks.pkl")

model = None
index = None
chunks = None


def get_embedding_model():
    global model
    if model is None:
        print("[VectorStore] Loading embedding model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def build_vectorstore():
    global index, chunks

    if os.path.exists(INDEX_FILE) and os.path.exists(CHUNKS_FILE):
        print("[VectorStore] Loading existing FAISS index from cache...")
        with open(INDEX_FILE, "rb") as f:
            index = pickle.load(f)
        with open(CHUNKS_FILE, "rb") as f:
            chunks = pickle.load(f)
        print(f"[VectorStore] Loaded {len(chunks)} chunks from cache")
        return

    print("[VectorStore] Building FAISS index...")
    docs = get_docs()
    chunks = docs

    embedding_model = get_embedding_model()
    print("[VectorStore] Generating embeddings...")
    embeddings = embedding_model.encode(chunks, show_progress_bar=True, batch_size=32)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    with open(INDEX_FILE, "wb") as f:
        pickle.dump(index, f)
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)

    print(f"[VectorStore] FAISS index built with {len(chunks)} chunks")


def retrieve(query: str, top_k: int = 5) -> list[str]:
    global index, chunks

    if index is None or chunks is None:
        build_vectorstore()

    embedding_model = get_embedding_model()
    query_embedding = embedding_model.encode([query]).astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])

    return results


def initialize():
    build_vectorstore()