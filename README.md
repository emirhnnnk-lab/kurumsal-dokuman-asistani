# Kurumsal Doküman Asistanı (yerel RAG)

> **EN summary:** Fully local RAG assistant for company documents: heading-aware chunking, hybrid search (vectors + Turkish stem overlap), a similarity threshold that refuses to answer when the documents don't cover the question, and cited sources in every answer. On a 16-question eval: 16/16 correct retrieval, 15/16 correct answers, 2/2 trap questions refused. Full English version: [README.en.md](README.en.md).

**Canlı demo:** [huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo](https://huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo), sekme: 📚 Doküman Asistanı. Demo OpenAI gpt-5.4-mini ile çalışıyor; iş mantığı bu repodakiyle aynı.

Her şirkette "izin hakkım kaç gün?", "masraf formunu kime göndereyim?" gibi soruların cevabı bir yerlerdeki bir PDF'te yazıyor, ama kimse o PDF'i bulamıyor. Bu asistan şirket belgelerini okuyup sorulara cevap veriyor. Benim için üç şart vardı:
- **Veri dışarı çıkmasın:** her şey kendi bilgisayarımda çalışıyor.
- **Her cevap kaynağını göstersin:** "bunu nereden çıkardın?" sorusunun cevabı hep hazır.
- **Bilmediğini uydurmasın:** belgelerde olmayan bir soruya "yer almıyor" desin.

## Nasıl çalışıyor
```
docs/ (MD, TXT, PDF) → başlıklara göre parçalara bölme → anlam vektörü (nomic-embed-text) → ChromaDB
Soru → karma arama (anlam + Türkçe kök eşleşmesi) → benzerlik eşiği → model (qwen2.5:3b) → cevap + [kaynak]
```
- **Başlık bağlamı:** her parça "Belge > Bölüm" başlığını yanında taşıyor. Böylece doğru parçayı bulmak kolaylaşıyor.
- **Karma arama:** Türkçede kelimeler ek alınca ("kaybolan" / "kaybı") anlam araması bazı eşleşmeleri kaçırıyor. Kelime köklerini karşılaştıran ikinci bir arama bunları yakalıyor.
- **Uydurmama:** soru belgelerle yeterince benzeşmiyorsa model hiç çağrılmıyor, doğrudan "dokümanlarda yer almıyor" cevabı dönüyor. Model çağrıldığında da sadece verilen parçalarla cevap vermeye zorlanıyor.

## Sonuçlar (16 soru, 2'si tuzak)
| Ölçü | Sonuç |
|---|---|
| Doğru kaynağı getirme (ilk 4 sonuçta) | **16/16** (sadece anlam aramasıyla 15/16) |
| Cevapta doğru bilgi | **15/16** |
| Tuzak sorularda uydurmama | **2/2** |

Aradaki 1 soru karma aramanın farkı: sadece anlam aramasıyla o soruda doğru parça gelmiyordu.

Tek yanlış cevap bir akıl yürütme hatası: 3B model doğru paragrafı bulduğu halde "7 yıllık kıdem" için yanlış aralığı seçti. Daha büyük bir model ya da kıdem tablosunu yapılandırılmış veriye çevirmek bu tür hatayı çözer. Ayrıntı: [eval/RAPOR.md](eval/RAPOR.md)

## Çalıştırma
```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b && ollama pull nomic-embed-text
uvicorn app.main:app --reload            # http://localhost:8000
curl -X POST localhost:8000/ingest       # docs/ klasörünü indeksler
python eval/degerlendir.py
pytest                                   # modelsiz birim testleri (sahte vektörlerle)
```
Docker dosyaları da hazır (`docker compose up`: Ollama + asistan). Dürüst not: Docker kurulumunu henüz baştan sona test etmedim; yukarıdaki yerel kurulum test edildi.

## Teknoloji
Python · FastAPI · ChromaDB · Ollama · nomic-embed-text · qwen2.5:3b · pypdf · pytest · Docker

> `docs/` içindeki politikalar uydurma bir şirkete (Örnek Teknoloji A.Ş.) ait.

---
Geliştiren: **Emirhan Karaca**
