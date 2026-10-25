FROM python:3.11-slim as base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

LABEL org.opencontainers.image.source="https://github.com/noemisoluri/progetto_devops.git"
LABEL org.opencontainers.image.description="Sentiment Analysis per recensioni - progetto master ProfessionAI"

# Installazione dipendenze di sistema minime
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# 1. Copia e installa prima le dipendenze Python (sfrutta la cache dei layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copia l'applicazione (incluso sentiment_analysis_model.pkl se è dentro la cartella app/)
COPY app ./app

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]