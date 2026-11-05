from . import config

SYSTEM = """Sen bir şirketin iç doküman asistanısın.
KURALLAR:
1. Sadece verilen BAĞLAM'daki bilgilere dayanarak cevap ver. Bağlamda yoksa "Bu bilgi dokümanlarda yer almıyor." de.
2. Rakamları, süreleri ve limitleri bağlamdaki gibi aynen yaz.
3. Her cevabın sonunda kullandığın kaynağı [dosya-adı] biçiminde belirt.
4. Kısa ve net cevap ver, Türkçe yaz."""


def answer(store, llm, question: str):
    hits = store.search(question)
    relevant = [h for h in hits if h["distance"] <= config.MAX_DISTANCE]
    if not relevant:
        return {"answer": "Bu bilgi dokümanlarda yer almıyor.", "sources": [], "grounded": False}
    context = "\n\n".join(f"[{h['source']}] {h['text']}" for h in relevant)
    text = llm.chat(SYSTEM, f"BAĞLAM:\n{context}\n\nSORU: {question}")
    sources = []
    for h in relevant:
        s = {"source": h["source"], "section": h["section"], "distance": h["distance"]}
        if s not in sources:
            sources.append(s)
    return {"answer": text, "sources": sources, "grounded": True}
