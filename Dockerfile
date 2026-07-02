# syntax=docker/dockerfile:1
FROM python:3.11-slim

RUN useradd -m -u 1000 user

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch first (avoids pulling 2GB of CUDA libs)
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.12.1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV HOME=/home/user

RUN chown -R user:user /app

ENV HF_HOME=/tmp/hf
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/sentence-transformers
ENV CHROMA_DIR=/tmp/chroma_db

EXPOSE 7860

USER user

CMD ["uvicorn", "app.Back_End.main:app", "--host", "0.0.0.0", "--port", "7860"]
