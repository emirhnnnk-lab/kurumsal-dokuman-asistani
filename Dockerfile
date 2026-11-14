# Küçük bir Python imajı
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# Bağımlılıklar önce kopyalanır: kod değişince bu katman önbellekten gelir
COPY requirements.txt .
RUN pip install -r requirements.txt

# Uygulama kodu ve örnek dokümanlar
COPY app app
COPY docs docs
COPY eval eval

# Root olmayan kullanıcı; vektör veritabanı /data altında tutulur
RUN useradd --create-home --uid 1000 uygulama \
    && mkdir /data && chown uygulama /data
USER uygulama

# Konteyner içinde Ollama'ya servis adıyla bağlan (yerelde varsayılan localhost kalır)
ENV OLLAMA_URL=http://ollama:11434 DB_DIR=/data/chroma
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
