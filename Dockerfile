# ===========================
# ---- BUILD STAGE ----
# ===========================
FROM python:3.11-slim AS builder

# Moins de .pyc et logs non bufferisés
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Outils de build nécessaires (uniquement dans le builder)
#    - build-essential / gcc : compiler des extensions C (ex. uvloop/httptools)
#    - libffi-dev / libssl-dev : headers pour dépendances crypto (OpenSSL) et FFI
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libffi-dev libssl-dev \
  && rm -rf /var/lib/apt/lists/*

# 2) Dépendances Python
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt


# ===========================
# ---- RUNTIME STAGE ----
# ===========================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# 1) On récupère les libs Python installées en --user depuis le builder
COPY --from=builder /root/.local /root/.local

# 2) On copie uniquement le code source de l'app
COPY src/ ./

# 3) Port exposé par Uvicorn
EXPOSE 8000

# 4) Démarrage : ENTRYPOINT = binaire fixe, CMD = arguments par défaut
ENTRYPOINT ["uvicorn", "app.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]