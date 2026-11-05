import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .ollama_client import Ollama
from .store import Store
from . import rag

app = FastAPI(title="Kurumsal Doküman Asistanı", version="1.0")
llm = Ollama()
store = Store(llm)


class Question(BaseModel):
    question: str


@app.post("/ingest")
def ingest():
    return {"chunks": store.ingest_dir()}


@app.post("/ask")
def ask(q: Question):
    return rag.answer(store, llm, q.question)


@app.get("/health")
def health():
    return {"ok": True, "chunks": store.col.count()}


@app.get("/", response_class=HTMLResponse)
def ui():
    return open(os.path.join(os.path.dirname(__file__), "ui.html"), encoding="utf-8").read()
