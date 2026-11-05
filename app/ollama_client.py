import httpx
from . import config


class Ollama:
    def __init__(self, url: str = config.OLLAMA_URL):
        self.url = url.rstrip("/")
        self.http = httpx.Client(timeout=180)

    def embed(self, texts):
        r = self.http.post(f"{self.url}/api/embed", json={"model": config.EMBED_MODEL, "input": texts})
        r.raise_for_status()
        return r.json()["embeddings"]

    def chat(self, system: str, user: str) -> str:
        r = self.http.post(f"{self.url}/api/chat", json={
            "model": config.CHAT_MODEL, "stream": False,
            "options": {"temperature": 0.1},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        })
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
