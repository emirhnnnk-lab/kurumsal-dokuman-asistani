import os
import chromadb
from . import config
from .chunker import chunk_document


class Store:
    def __init__(self, llm, db_dir: str = config.DB_DIR):
        self.llm = llm
        self.client = chromadb.PersistentClient(path=db_dir)
        self.col = self.client.get_or_create_collection(config.COLLECTION, metadata={"hnsw:space": "cosine"})

    def reset(self):
        self.client.delete_collection(config.COLLECTION)
        self.col = self.client.get_or_create_collection(config.COLLECTION, metadata={"hnsw:space": "cosine"})

    def ingest_dir(self, docs_dir: str = config.DOCS_DIR):
        self.reset()
        n = 0
        for name in sorted(os.listdir(docs_dir)):
            path = os.path.join(docs_dir, name)
            text = read_any(path)
            if not text:
                continue
            chunks = chunk_document(text, name, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
            vecs = self.llm.embed([c.text for c in chunks])
            self.col.add(
                ids=[f"{name}#{c.index}" for c in chunks],
                documents=[c.text for c in chunks],
                embeddings=vecs,
                metadatas=[{"source": c.source, "section": c.section} for c in chunks],
            )
            n += len(chunks)
        return n

    def search(self, query: str, k: int = config.TOP_K):
        """Hibrit arama: vektör benzerliği + kelime kökü örtüşmesi ile yeniden sıralama.
        Türkçe çekim ekleri ('kaybolan' / 'kaybı') için ilk 5 harf kök kabul edilir."""
        q = self.llm.embed([query])[0]
        n = min(max(k * 3, 8), self.col.count() or 1)
        r = self.col.query(query_embeddings=[q], n_results=n)
        qk = koklar(query)
        hits = []
        for d, m, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
            ortusme = len(qk & koklar(d)) / (len(qk) or 1)
            hits.append({"text": d, "source": m["source"], "section": m["section"], "distance": round(dist, 3),
                         "skor": round((1 - dist) + 0.35 * ortusme, 3)})
        return sorted(hits, key=lambda h: -h["skor"])[:k]


DUR = {"nedir", "kadar", "olan", "için", "nasıl", "hangi", "mıdır", "midir", "sonra", "önce", "fazla", "bir", "veya", "olarak"}


def koklar(t: str):
    import re
    return {w[:5] for w in re.findall(r"[a-zçğıöşü]{4,}", t.lower().replace("i̇", "i")) if w not in DUR}


def read_any(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".md", ".txt"):
        return open(path, encoding="utf-8").read()
    if ext == ".pdf":
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    return ""
