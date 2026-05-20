FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch
RUN pip install \
    beautifulsoup4 \
    cloudscraper \
    faiss-cpu \
    fastapi \
    "langchain>=0.2.0" \
    "langchain-community>=0.2.0" \
    "langchain-deepseek>=1.0.1" \
    "langchain-huggingface>=0.0.3" \
    lxml \
    pandas \
    python-dotenv \
    requests \
    sentence-transformers \
    "uvicorn[standard]>=0.27.0"

COPY backend/ backend/
COPY frontend/ frontend/
COPY data/ data/
COPY db/ db/
COPY assets/ assets/
COPY .env .env
COPY command.txt command.txt

EXPOSE 8000

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
