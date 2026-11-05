import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
DB_DIR = os.getenv("DB_DIR", os.path.join(os.path.dirname(__file__), "..", ".chroma"))
DOCS_DIR = os.getenv("DOCS_DIR", os.path.join(os.path.dirname(__file__), "..", "docs"))
COLLECTION = "dokumanlar"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K = 4
# Kosinüs mesafesi bu değerin üstündeyse "ilgili belge yok" sayılır (uydurma cevabı engeller)
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "0.38"))
