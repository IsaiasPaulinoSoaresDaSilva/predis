from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
from typing import Dict

from backend.data_management.data_manager import DataManager

# --- Pydantic Models Definition ---
class PredictionInput(BaseModel):
    region: str = 'sudeste'

class PredictionResponse(BaseModel):
    risk_level: int
    risk_probability: float
    feature_importance: Dict[str, float]
    message: str | None = None

# --- Application Initialization ---
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

try:
    model_data = joblib.load('backend/disaster_model.joblib')
    model = model_data['model']
    model_features = model_data['features']
except FileNotFoundError:
    print("AVISO: Arquivo do modelo ('disaster_model.joblib') não encontrado.")
    print("Execute o script 'model.py' primeiro para treinar e salvar o modelo.")
    model = None

data_manager = DataManager()

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Previsão de Desastres v2 (IA Melhorada)"}

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
        if df.empty or len(df) < 3:
            return PredictionResponse(
                risk_level=0, risk_probability=0, feature_importance={},
                message="Dados insuficientes para a região."
            )

        df = df.sort_values('data').reset_index(drop=True)

        # 2. Engenharia de Features para o dia mais recente
        last_day_df = df.iloc[[-1]].copy()

        last_day_df['precipitacao_acumulada_3d'] = df['precipitacao_mm'].rolling(window=3).sum().iloc[-1]
        last_day_df['precipitacao_max_3d'] = df['precipitacao_mm'].rolling(window=3).max().iloc[-1]
        last_day_df['media_movel_nivel_rio_3d'] = df['nivel_rio_m'].rolling(window=3).mean().iloc[-1]
        last_day_df['variacao_nivel_rio_1d'] = df['nivel_rio_m'].diff().iloc[-1]

        # Garantir que as features estão na ordem correta
        # Lidar com colunas faltantes que o modelo espera
        for col in model_features:
            if col not in last_day_df:
                last_day_df[col] = 0
        features_for_prediction = last_day_df[model_features]

        # 3. Fazer a Predição
        predicted_class = model.predict(features_for_prediction)[0]
        probabilities = model.predict_proba(features_for_prediction)[0]
        
        # A probabilidade de risco é a soma das probabilidades das classes de risco (ex: 1 e 2)
        risk_probability = probabilities[1:].sum()

        # 4. Obter a importância das features
        importances = model.feature_importances_
        feature_importance = {feature: importance for feature, importance in zip(model_features, importances)}

        return PredictionResponse(
            risk_level=int(predicted_class),
            risk_probability=float(risk_probability),
            feature_importance=feature_importance
        )
    except Exception as e:
        return PredictionResponse(
            risk_level=-1, risk_probability=0, feature_importance={},
            message=f"Erro na predição: {e}"
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
        return {"error": f"Um erro inesperado ocorreu: {str(e)}"}
