# syntax=docker/dockerfile:1
FROM python:3.11-slim

RUN useradd -m -u 1000 user

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/run/nginx /etc/nginx/sites-enabled

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

RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

COPY <<'EOF' /etc/nginx/sites-available/knowmate.conf
server {
    listen 7860;
    client_max_body_size 50M;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 600s;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF

RUN ln -sf /etc/nginx/sites-available/knowmate.conf /etc/nginx/sites-enabled/

COPY <<'EOF' /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
user=root

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:uvicorn]
command=uvicorn app.Back_End.main:app --host 127.0.0.1 --port 8000
user=user
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
