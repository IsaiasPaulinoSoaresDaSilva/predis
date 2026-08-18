#!/bin/sh
# Treina o modelo se ainda não existir (ex.: primeiro start, ou volume novo)
# e então inicia a API. Ver backend/Dockerfile.
set -e

if [ ! -f "backend/data/disaster_model.joblib" ]; then
    echo "INFO: disaster_model.joblib não encontrado — treinando o modelo antes de iniciar a API..."
    python -m backend.model
fi

exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
