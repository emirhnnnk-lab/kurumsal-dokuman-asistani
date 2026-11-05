"""Belgeleri başlık farkındalıklı parçalara böler."""
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str
    section: str
    index: int


def split_sections(md: str):
    """Markdown'ı '## ' başlıklarına göre bölümlere ayırır. (başlık, metin) döner."""
    title = ""
    m = re.search(r"^# (.+)$", md, re.M)
    if m:
        title = m.group(1).strip()
    parts = re.split(r"^## ", md, flags=re.M)
    out = []
    head = parts[0].replace(f"# {title}", "").strip() if title else parts[0].strip()
    if head:
        out.append((title or "Giriş", head))
    for p in parts[1:]:
        lines = p.split("\n", 1)
        out.append((lines[0].strip(), lines[1].strip() if len(lines) > 1 else ""))
    return title, out


def chunk_text(text: str, size: int, overlap: int):
    """Uzun metni kelime sınırında, örtüşmeli parçalara böler."""
    if len(text) <= size:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            sp = text.rfind(" ", start, end)
            if sp > start + size // 2:
                end = sp
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def chunk_document(md: str, source: str, size: int = 700, overlap: int = 120):
    title, sections = split_sections(md)
    result, i = [], 0
    for sec, body in sections:
        for piece in chunk_text(body, size, overlap):
            # Başlık bağlamı parçaya eklenir: "İzin Politikası > Devreden izin: ..."
            result.append(Chunk(f"{title} > {sec}\n{piece}", source, sec, i))
            i += 1
    return result
