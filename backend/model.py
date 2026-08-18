import os
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
import joblib
from backend.data_management.data_manager import DataManager
from backend.feature_engineering import FEATURES, add_rolling_features, compute_risk

# --- Estudo de caso: São José dos Campos (SP) ---
# O modelo é treinado com dados agregados das 6 regiões administrativas do
# município (Centro, Norte, Sul, Leste, Oeste, Sudeste — ver
# frontend/src/assets/sjc-regions.json e backend/data_management/data_manager.py).
# Cada região tem sua própria série histórica REAL (precipitação real via
# Open-Meteo Archive + nível derivado da estação real da ANA em SJC — ver
# backend/scripts/generate_sjc_data.py e backend/connectors/), com fallback
# de conexão ao vivo às mesmas séries reais mais recentes.
SJC_REGIONS = ['centro', 'norte', 'sul', 'leste', 'oeste', 'sudeste']

print("INFO: Coletando e combinando dados de todas as regiões de São José dos Campos via DataManager...")
data_manager = DataManager()

region_dfs = []
for region_id in SJC_REGIONS:
    try:
        region_df = data_manager.get_combined_data(region_id)
        if region_df.empty:
            print(f"AVISO: DataManager retornou vazio para a região '{region_id}'. Pulando.")
            continue
        region_df = region_df.sort_values('data').reset_index(drop=True)
        # Features de janela móvel calculadas ANTES de concatenar com as
        # outras regiões, para não misturar o histórico de uma região com o
        # de outra nas bordas das séries.
        region_df = add_rolling_features(region_df)
        region_df['regiao'] = region_id
        region_dfs.append(region_df)
    except Exception as e:
        print(f"AVISO: falha ao coletar dados da região '{region_id}': {e}")

if not region_dfs:
    print("ERRO: Não foi possível coletar dados de nenhuma região de São José dos Campos.")
    exit()

print("INFO: Engenharia de features aplicada por região (ver loop acima).")
df = pd.concat(region_dfs, ignore_index=True)

# As janelas móveis usam min_periods=1 (ver feature_engineering.py) — nenhum
# NaN é produzido de fato, então nenhuma linha é descartada aqui. Mantido
# como checagem defensiva explícita (não um dropna() silencioso).
n_before = len(df)
df = df.dropna(subset=FEATURES).reset_index(drop=True)
if len(df) != n_before:
    print(f"AVISO: {n_before - len(df)} linha(s) descartada(s) por NaN inesperado nas features.")
else:
    print("INFO: nenhuma linha descartada — todas as janelas móveis usam min_periods=1.")

# --- Definição de Risco Granular ---
# Limiares calibrados empiricamente sobre os datasets das 6 regiões de SJC
# (ver backend/scripts/generate_sjc_data.py), de forma a produzir uma
# distribuição de classes plausível e coerente com o risco relatado
# publicamente por região (Leste/Sul mais expostas, Norte/Oeste menos — ver
# CASE_STUDY_SJC.md). Definição em backend/feature_engineering.py.
df['risco'] = compute_risk(df)  # 0=baixo, 1=moderado, 2=alto

# --- Treinamento do Modelo: ensemble de 2 classificadores ---
# Combina RandomForest (bagging, robusto a ruído/outliers) com
# GradientBoosting (boosting, geralmente melhor AUC em tabular pequeno/médio)
# via voto suave (média das probabilidades) — nenhum dos dois "descarta" a
# opinião do outro, a predição final usa os dois. Ver IMPLEMENTATION_PLAN.md
# ("como aumentar AUC") para o racional de não usar um único modelo.
print("INFO: Treinando o modelo de IA (ensemble RandomForest + GradientBoosting)...")
features = FEATURES
target = 'risco'

X = df[features]
y = df[target]

print(f"\nDataset de treino: {len(df)} dias-região (6 regiões de São José dos Campos combinadas).")
print("Distribuição das classes de risco no dataset de treino:")
print(y.value_counts())
print("\nDistribuição de risco por região:")
print(df.groupby('regiao')['risco'].value_counts().unstack(fill_value=0))

if len(y.unique()) < 2:
    print("\nAviso: Os dados não contêm exemplos suficientes para pelo menos duas classes de risco. Saindo.")
    exit()

rf = RandomForestClassifier(n_estimators=150, random_state=42, class_weight='balanced')
gb = GradientBoostingClassifier(n_estimators=150, random_state=42)
ensemble = VotingClassifier(estimators=[('rf', rf), ('gb', gb)], voting='soft')

# --- Validação cruzada estratificada (mais robusta que um único holdout de
# 25%, que com ~600 linhas deixaria só ~150 no teste) ---
n_splits = min(5, y.value_counts().min())  # cada classe precisa de >= n_splits exemplos
if n_splits >= 2:
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    cv_proba = cross_val_predict(ensemble, X, y, cv=cv, method='predict_proba')
    cv_pred = cv_proba.argmax(axis=1)
    try:
        if len(np.unique(y)) == 2:
            # roc_auc_score binário espera a probabilidade da classe positiva
            # (coluna 1), não a matriz (n, 2) inteira — e não aceita multi_class.
            cv_auc = roc_auc_score(y, cv_proba[:, 1])
        else:
            cv_auc = roc_auc_score(y, cv_proba, multi_class='ovr', average='macro')
    except ValueError as e:
        cv_auc = float('nan')
        print(f"AVISO: não foi possível calcular AUC por validação cruzada: {e}")
    print(f"\nValidação cruzada estratificada ({n_splits} folds) — AUC: {cv_auc:.4f}")
    print(classification_report(y, cv_pred, zero_division=0))
else:
    print("\nAVISO: classes com poucos exemplos demais para validação cruzada — pulando.")

# --- Split final para o relatório de classificação "tradicional" (e para
# manter um conjunto de teste nunca visto pelo modelo salvo) ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
ensemble.fit(X_train, y_train)
y_pred = ensemble.predict(X_test)
print("\nRelatório de Classificação do Modelo (holdout 25%, estudo de caso: São José dos Campos):")
print(classification_report(y_test, y_pred, zero_division=0))

# --- Modelo final: treinado em 100% dos dados (o holdout acima já validou
# a generalização; para servir em produção, usamos todo o histórico) ---
ensemble.fit(X, y)

# VotingClassifier não expõe feature_importances_ (é heterogêneo — GB e RF
# têm escalas de importância diferentes). Calculamos manualmente uma média
# simples dos dois, para o painel de XAI do frontend continuar funcionando.
rf_fitted = ensemble.named_estimators_['rf']
gb_fitted = ensemble.named_estimators_['gb']
avg_importances = (rf_fitted.feature_importances_ + gb_fitted.feature_importances_) / 2
feature_importances = dict(zip(features, avg_importances))

model_data = {
    'model': ensemble,
    'features': features,
    'feature_importances': feature_importances,
    'case_study': 'sao_jose_dos_campos',
    'regions': SJC_REGIONS,
}

MODEL_PATH = 'backend/data/disaster_model.joblib'
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model_data, MODEL_PATH)

print(f"\nModelo (ensemble RF+GB) treinado com dados de São José dos Campos e salvo em '{MODEL_PATH}'")
