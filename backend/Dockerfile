# Dockerfile do backend do PreDis (FastAPI + modelo scikit-learn).
# Contexto de build esperado: a RAIZ do repositório (não backend/), porque o
# código usa imports absolutos `backend.xxx` — ver docker-compose.yml.
FROM python:3.11-slim

WORKDIR /app

# Dependências primeiro (cache de camada do Docker)
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Código da aplicação
COPY backend/ backend/

# Se disaster_model.joblib não existir na imagem, o entrypoint treina o
# modelo no primeiro start do container (ver docker-entrypoint.sh). Isso
# evita depender de rede durante `docker build` e mantém o modelo
# reproduzível a partir dos datasets versionados em backend/historical_data/.
RUN chmod +x backend/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["backend/docker-entrypoint.sh"]
