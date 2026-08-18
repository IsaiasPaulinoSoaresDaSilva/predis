import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import database
from backend.data_management.data_manager import DataManager
from backend.feature_engineering import add_rolling_features, ensure_feature_columns

logger = logging.getLogger("predis")
logging.basicConfig(level=logging.INFO)


# --- Pydantic Models Definition ---
class PredictionInput(BaseModel):
    region: str = 'centro'  # região padrão do estudo de caso (São José dos Campos)

class PredictionResponse(BaseModel):
    risk_level: int
    risk_probability: float
    feature_importance: Dict[str, float]
    message: str | None = None

class PredictionRecord(BaseModel):
    id: int
    region: str
    created_at: str
    risk_level: int
    risk_probability: float
    feature_importance: Dict[str, float]
    message: str | None = None

# --- Application Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(lifespan=lifespan)

# CORS: em desenvolvimento local, aceitar qualquer origem (padrão "*").
# Para um deploy real, defina a env var ALLOWED_ORIGINS com uma lista
# separada por vírgulas (ex.: "https://meusite.com,https://outro.com") —
# ver IMPLEMENTATION_PLAN.md, Fase 3 ("Revisar CORS antes de qualquer
# deploy público").
_allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "*")
allowed_origins = ["*"] if _allowed_origins_env == "*" else [
    origin.strip() for origin in _allowed_origins_env.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = 'backend/data/disaster_model.joblib'

try:
    model_data = joblib.load(MODEL_PATH)
    model = model_data['model']
    model_features = model_data['features']
    # Pré-calculado no treino (backend/model.py): VotingClassifier (ensemble
    # RandomForest + GradientBoosting) não expõe feature_importances_ nativamente.
    model_feature_importances = model_data.get('feature_importances', {})
except FileNotFoundError:
    logger.warning("Arquivo do modelo ('%s') não encontrado.", MODEL_PATH)
    logger.warning("Execute 'python -m backend.model' primeiro para treinar e salvar o modelo.")
    model = None
    model_features = []
    model_feature_importances = {}

data_manager = DataManager()


def _persist_prediction(region: str, response: PredictionResponse) -> None:
    """Salva a predição no histórico. Nunca deve derrubar a resposta da API
    — falha de persistência é registrada em log e ignorada."""
    try:
        database.save_prediction(
            region=region,
            risk_level=response.risk_level,
            risk_probability=response.risk_probability,
            feature_importance=response.feature_importance,
            message=response.message,
        )
    except Exception:
        logger.exception("Falha ao persistir predição para a região '%s'", region)


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do PreDis — Estudo de Caso: São José dos Campos (SP)"}


@app.post("/predict", response_model=PredictionResponse)
def predict(data: PredictionInput):
    """
    Usa o modelo de IA treinado para prever o risco de desastre
    para a região especificada.
    """
    if not model:
        return PredictionResponse(
            risk_level=0, risk_probability=0, feature_importance={},
            message="Modelo de IA não carregado."
        )

    try:
        # 1. Obter todos os dados para a região usando o DataManager
        df = data_manager.get_combined_data(region_id=data.region)
    except Exception as e:
        logger.exception("Falha ao buscar dados para a região '%s'", data.region)
        return PredictionResponse(
            risk_level=-1, risk_probability=0, feature_importance={},
            message=f"Não foi possível obter dados para a região '{data.region}': {e}"
        )

    if df.empty or len(df) < 3:
        response = PredictionResponse(
            risk_level=0, risk_probability=0, feature_importance={},
            message="Dados insuficientes para a região."
        )
        _persist_prediction(data.region, response)
        return response

    try:
        df = df.sort_values('data').reset_index(drop=True)

        # 2. Engenharia de Features para o dia mais recente
        # (usa exatamente a mesma lógica de backend/model.py durante o
        # treino — ver backend/feature_engineering.py)
        df = add_rolling_features(df)
        last_day_df = ensure_feature_columns(df.iloc[[-1]].copy(), model_features)
        features_for_prediction = last_day_df[model_features]

        # 3. Fazer a Predição
        predicted_class = model.predict(features_for_prediction)[0]
        probabilities = model.predict_proba(features_for_prediction)[0]

        # A probabilidade de risco é a soma das probabilidades das classes de risco (ex: 1 e 2)
        risk_probability = probabilities[1:].sum()

        # 4. Obter a importância das features (pré-calculada no treino — ver
        # backend/model.py, o ensemble não expõe feature_importances_ direto)
        feature_importance = {
            feature: float(model_feature_importances.get(feature, 0.0)) for feature in model_features
        }

        response = PredictionResponse(
            risk_level=int(predicted_class),
            risk_probability=float(risk_probability),
            feature_importance=feature_importance
        )
        _persist_prediction(data.region, response)
        return response
    except KeyError as e:
        logger.exception("Coluna/feature ausente ao montar a predição para '%s'", data.region)
        return PredictionResponse(
            risk_level=-1, risk_probability=0, feature_importance={},
            message=f"Dado ausente para a predição (coluna {e}). O modelo pode estar desatualizado em relação aos dados."
        )
    except ValueError as e:
        logger.exception("Valor inválido ao montar a predição para '%s'", data.region)
        return PredictionResponse(
            risk_level=-1, risk_probability=0, feature_importance={},
            message=f"Valor inválido nos dados da região: {e}"
        )
    except Exception as e:
        logger.exception("Erro inesperado na predição para '%s'", data.region)
        return PredictionResponse(
            risk_level=-1, risk_probability=0, feature_importance={},
            message=f"Erro inesperado na predição: {e}"
        )


@app.get("/historical_data")
def get_historical_data(region: str = 'default'):
    """
    Serve os dados históricos para uma região específica, orquestrando
    a busca através do DataManager.
    """
    try:
        df = data_manager.get_combined_data(region_id=region)
        if df.empty:
            return {"error": f"Não foi possível obter dados combinados para a região '{region}'."}
        return df.to_dict(orient='records')
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        logger.exception("Erro inesperado ao buscar dados históricos para '%s'", region)
        return {"error": f"Um erro inesperado ocorreu: {str(e)}"}


@app.get("/predictions", response_model=List[PredictionRecord])
def get_predictions(region: Optional[str] = None, limit: int = 50):
    """
    Retorna o histórico de predições já realizadas (persistidas em SQLite),
    mais recente primeiro. Ver backend/database.py e
    IMPLEMENTATION_PLAN.md (Fase 2 — Persistência).
    """
    return database.get_predictions(region=region, limit=limit)
