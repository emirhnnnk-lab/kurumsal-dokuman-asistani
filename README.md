# Kurumsal Doküman Asistanı (Lokal RAG)

**🔴 Canlı demo:** [huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo](https://huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo) — sekme: 📚 Doküman Asistanı (demo OpenAI gpt-5.4-mini ile çalışır; iş mantığı bu repodakiyle aynı)

Şirket dokümanlarını **tamamen lokalde** sorgulayan asistan: veri buluta gitmez, her cevap kaynak gösterir, dokümanda olmayan soruya uydurmaz.

## Mimari
```
docs/ (MD, TXT, PDF) → başlık farkındalıklı parçalama → embedding (nomic-embed-text) → ChromaDB
Soru → hibrit arama (vektör + Türkçe kök örtüşmesi) → mesafe eşiği → LLM (qwen2.5:3b) → cevap + [kaynak]
```
- **Başlık bağlamı:** her parça "Belge > Bölüm" başlığını taşır, geri getirme isabeti artar.
- **Hibrit arama:** Türkçe çekim eklerinde ("kaybolan" / "kaybı") vektör aramanın kaçırdığı eşleşmeleri kök örtüşmesiyle yakalar.
- **Uydurmama:** benzerlik eşiğinin altında kalan sorularda LLM çağrılmadan "dokümanlarda yer almıyor" döner; LLM de yalnızca bağlamla cevap vermeye zorlanır.

## Sonuçlar (16 soru, 2'si tuzak)
| Ölçüt | Sonuç |
|---|---|
| Doğru kaynağı getirme (hit@4) | **16/16** (yalnız vektör aramada 15/16) |
| Cevapta doğru bilgi | **15/16** |
| Tuzak sorularda uydurmama | **2/2** |

Tek hata bir akıl yürütme hatası: 3B model doğru paragrafı bulmasına rağmen "7 yıllık kıdem" için yanlış aralığı seçti. Daha büyük model ya da kıdem tablosunu yapılandırılmış veriye çevirmek bu tür hataları çözer. Ayrıntı: [eval/RAPOR.md](eval/RAPOR.md)

## Çalıştırma
```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b && ollama pull nomic-embed-text
uvicorn app.main:app --reload            # http://localhost:8000
curl -X POST localhost:8000/ingest       # docs/ klasörünü indeksler
python eval/degerlendir.py
pytest                                   # LLM'siz birim testleri (sahte embedding)
```
Docker ile: `docker compose up` (Ollama + asistan).

## Teknoloji
Python · FastAPI · ChromaDB · Ollama · nomic-embed-text · qwen2.5:3b · pypdf · pytest · Docker

> `docs/` içindeki politikalar uydurma bir şirkete (Örnek Teknoloji A.Ş.) aittir.

---
Geliştiren: **Emirhan Karaca**
