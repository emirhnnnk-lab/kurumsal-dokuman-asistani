"""LLM'siz test: sahte embedding ile geri getirme ve 'uydurmama' kuralı."""
import tempfile
from app.store import Store
from app import rag


class FakeLLM:
    VOCAB = ["izin", "masraf", "yangın", "ofis", "asansör", "yemek"]

    def embed(self, texts):
        return [[float(t.lower().count(w)) + 0.01 for w in self.VOCAB] for t in texts]

    def chat(self, system, user):
        return "CEVAP: " + user.split("SORU:")[-1].strip()


def make_store(tmp):
    import os
    d = os.path.join(tmp, "docs"); os.makedirs(d)
    open(os.path.join(d, "a.md"), "w", encoding="utf-8").write("# A\n## İzin\nYıllık izin izin izin 14 gün.")
    open(os.path.join(d, "b.md"), "w", encoding="utf-8").write("# B\n## Yangın\nYangında asansör kullanılmaz. yangın yangın")
    s = Store(FakeLLM(), db_dir=os.path.join(tmp, "db"))
    assert s.ingest_dir(d) == 2
    return s


def test_dogru_belgeyi_getirir():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        s = make_store(tmp)
        assert s.search("izin kaç gün", k=1)[0]["source"] == "a.md"
        assert s.search("yangında asansör", k=1)[0]["source"] == "b.md"


def test_ilgisiz_soruda_uydurmaz(monkeypatch):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        s = make_store(tmp)
        monkeypatch.setattr("app.config.MAX_DISTANCE", 0.05)
        r = rag.answer(s, FakeLLM(), "hisse senedi fiyatı")
        assert r["grounded"] is False and r["sources"] == []
