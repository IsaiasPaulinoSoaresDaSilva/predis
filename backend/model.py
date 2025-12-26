import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import numpy as np
from backend.data_management.data_manager import DataManager

# --- Coleta de Dados via DataManager ---
print("INFO: Coletando e combinando dados de todas as fontes via DataManager...")
data_manager = DataManager()
# Para o treinamento, usamos uma região padrão (ex: sudeste) para gerar o modelo base.
# Uma abordagem mais avançada poderia treinar um modelo por região.
try:
    df = data_manager.get_combined_data('sudeste')
    if df.empty:
        raise ValueError("O DataManager retornou um DataFrame vazio.")
    df = df.sort_values('data').reset_index(drop=True)
except Exception as e:
    print(f"ERRO: Não foi possível coletar dados para o treinamento. {e}")
    exit()

# --- Engenharia de Features Avançada ---
print("INFO: Realizando engenharia de features...")
# 1. Features baseadas em precipitação histórica
df['precipitacao_acumulada_3d'] = df['precipitacao_mm'].rolling(window=3, min_periods=1).sum()
df['precipitacao_max_3d'] = df['precipitacao_mm'].rolling(window=3, min_periods=1).max()

# 2. Features baseadas no nível do rio histórico
df['media_movel_nivel_rio_3d'] = df['nivel_rio_m'].rolling(window=3, min_periods=1).mean()
df['variacao_nivel_rio_1d'] = df['nivel_rio_m'].diff().fillna(0)

# Remover valores NaN gerados pelas janelas móveis
df = df.dropna().reset_index(drop=True)

# --- Definição de Risco Granular ---
conditions = [
    (df['precipitacao_acumulada_3d'] > 150) & (df['nivel_rio_m'] > 6.5) | (df['previsao_chuva_d1'] > 50),
    (df['precipitacao_acumulada_3d'] > 80) | (df['nivel_rio_m'] > 5.0) | (df['previsao_chuva_d1'] > 25),
]
choices = [2, 1] # 2 para Alto Risco, 1 para Risco Moderado
df['risco'] = np.select(conditions, choices, default=0) # 0 para Baixo Risco

# --- Treinamento do Modelo ---
print("INFO: Treinando o modelo de IA...")
features = [
    'precipitacao_mm', 
    'nivel_rio_m',
    'precipitacao_acumulada_3d',
    'precipitacao_max_3d',
    'media_movel_nivel_rio_3d',
    'variacao_nivel_rio_1d',
    'previsao_chuva_d1', # <-- Nova feature!
    'previsao_chuva_d2', # <-- Nova feature!
    'previsao_chuva_d3'  # <-- Nova feature!
]
target = 'risco'

X = df[features]
y = df[target]

print("\nDistribuição das classes de risco no dataset de treino:")
print(y.value_counts())

if len(y.unique()) < 2:
    print("\nAviso: Os dados não contêm exemplos suficientes para pelo menos duas classes de risco. Saindo.")
    exit()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=150, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("\nRelatório de Classificação do Modelo (com dados de previsão):")
print(classification_report(y_test, y_pred, zero_division=0))

model_data = {
    'model': model,
    'features': features
}

joblib.dump(model_data, 'backend/disaster_model.joblib')

print("\nModelo treinado com features de previsão e salvo com sucesso em 'backend/disaster_model.joblib'")
