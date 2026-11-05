from app.chunker import chunk_document, chunk_text, split_sections

DOC = "# Politika\n\n## Bir\nKısa metin.\n\n## İki\n" + ("kelime " * 300)


def test_split_sections_baslik_ve_bolumler():
    title, secs = split_sections(DOC)
    assert title == "Politika"
    assert [s[0] for s in secs] == ["Bir", "İki"]


def test_chunk_text_ortusme_ve_sinir():
    parts = chunk_text("a " * 1000, 200, 40)
    assert len(parts) > 5
    assert all(len(p) <= 200 for p in parts)


def test_parcalar_baslik_baglami_tasir():
    chunks = chunk_document(DOC, "x.md", 300, 50)
    assert chunks[0].text.startswith("Politika > Bir")
    assert all(c.source == "x.md" for c in chunks)
    assert len({c.index for c in chunks}) == len(chunks)
