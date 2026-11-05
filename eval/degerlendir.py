"""RAG değerlendirmesi: geri getirme isabeti (hit@k), cevap doğruluğu ve 'bilmiyorum' doğruluğu."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.ollama_client import Ollama
from app.store import Store
from app import rag

qs = json.load(open(os.path.join(os.path.dirname(__file__), "sorular.json"), encoding="utf-8"))
llm = Ollama(); store = Store(llm)
if store.col.count() == 0:
    store.ingest_dir()
rows, hit, correct, t0 = [], 0, 0, time.time()
for q in qs:
    r = rag.answer(store, llm, q["soru"])
    srcs = [s["source"] for s in r["sources"]]
    h = (q["kaynak"] in srcs) if q["kaynak"] else (not r["grounded"] or any(b in r["answer"].lower() for b in q["beklenen"]))
    ok = any(b.lower() in r["answer"].lower() for b in q["beklenen"])
    hit += h; correct += ok
    rows.append(f"| {q['soru']} | {'✅' if h else '❌'} | {'✅' if ok else '❌'} | {r['answer'][:90].replace('|','/').replace(chr(10),' ')} |")
n = len(qs)
rep = [f"# Değerlendirme raporu", "", f"- Soru sayısı: **{n}** (2'si dokümanlarda olmayan tuzak soru)",
       f"- Doğru kaynağı getirme (hit@4): **{hit}/{n}**", f"- Cevapta beklenen bilgi: **{correct}/{n}**",
       f"- Model: `{os.getenv('CHAT_MODEL','qwen2.5:3b')}` · Embedding: `nomic-embed-text` · Süre: {time.time()-t0:.0f} sn", "",
       "| Soru | Kaynak | Cevap | Model cevabı (kısaltılmış) |", "|---|---|---|---|"] + rows
open(os.path.join(os.path.dirname(__file__), "RAPOR.md"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
print(f"hit@4 {hit}/{n}  dogru {correct}/{n}")
