"""
Engenharia de features compartilhada entre o treino (backend/model.py) e a
inferência (backend/main.py). Antes esta lógica estava duplicada nos dois
arquivos — risco real de os dois divergirem silenciosamente a cada mudança.
Ver IMPLEMENTATION_PLAN.md, Fase 3 ("Robustez de backend").
"""
import pandas as pd

# Ordem/lista de features usada pelo modelo. Mantida em um único lugar para
# que backend/model.py (treino) e backend/main.py (inferência) nunca fiquem
# fora de sincronia.
FEATURES = [
    'precipitacao_mm',
    'nivel_rio_m',
    'precipitacao_acumulada_3d',
    'precipitacao_max_3d',
    'media_movel_nivel_rio_3d',
    'variacao_nivel_rio_1d',
    'subida_rio_14d',
    'previsao_chuva_d1',
    'previsao_chuva_d2',
    'previsao_chuva_d3',
]

# Limiares de risco, calibrados empiricamente sobre a distribuição real dos
# dados de São José dos Campos (ver backend/scripts/generate_sjc_data.py —
# precipitação real via Open-Meteo Archive + nível via estação real da ANA).
# Recalibrados em 18/08/2026 ao trocar os dados sintéticos por reais: a
# correlação entre chuva local (por região) e o nível da única estação real
# da ANA é fraca (a estação é uma barragem, seu nível reflete a operação do
# reservatório, não só a chuva local — ver ana_connector.py), então usamos
# OR entre os sinais (não AND) para não exigir que ambos disparem juntos.
# `subida_rio_14d` foi escolhida no lugar de um limiar absoluto de
# `nivel_rio_m` porque as regiões do estudo de caso representam cursos
# d'água de portes diferentes.
RISK_ALTO_PRECIP_ACC_3D = 56  # ~percentil 95 do histórico real
RISK_ALTO_SUBIDA_RIO_14D = 0.14  # ~percentil 95
RISK_ALTO_PREVISAO_D1 = 45
RISK_MODERADO_PRECIP_ACC_3D = 35  # ~percentil 80
RISK_MODERADO_SUBIDA_RIO_14D = 0.07  # ~percentil 75
RISK_MODERADO_PREVISAO_D1 = 20


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona as features de janela móvel a um DataFrame de UMA única região,
    já ordenado por data ascendente. Não deve ser chamada sobre dados de
    múltiplas regiões concatenadas sem agrupar antes (ver uso com
    `groupby` em backend/model.py) — misturaria o histórico de uma região
    com o de outra nas bordas da série.

    Espera as colunas 'precipitacao_mm' e 'nivel_rio_m'. Retorna uma cópia
    com as colunas adicionais:
      - precipitacao_acumulada_3d, precipitacao_max_3d
      - media_movel_nivel_rio_3d, variacao_nivel_rio_1d
      - subida_rio_14d (nível atual - mínima dos últimos 14 dias)
    """
    df = df.copy()
    df['precipitacao_acumulada_3d'] = df['precipitacao_mm'].rolling(window=3, min_periods=1).sum()
    df['precipitacao_max_3d'] = df['precipitacao_mm'].rolling(window=3, min_periods=1).max()
    df['media_movel_nivel_rio_3d'] = df['nivel_rio_m'].rolling(window=3, min_periods=1).mean()
    df['variacao_nivel_rio_1d'] = df['nivel_rio_m'].diff().fillna(0)
    df['subida_rio_14d'] = df['nivel_rio_m'] - df['nivel_rio_m'].rolling(window=14, min_periods=1).min()
    return df


def compute_risk(df: pd.DataFrame):
    """
    Deriva a classe de risco (0=baixo, 1=moderado, 2=alto) a partir das
    features já calculadas por `add_rolling_features`. Requer também a
    coluna 'previsao_chuva_d1'. Retorna uma Series de inteiros.
    """
    import numpy as np

    conditions = [
        (df['precipitacao_acumulada_3d'] > RISK_ALTO_PRECIP_ACC_3D)
        | (df['subida_rio_14d'] > RISK_ALTO_SUBIDA_RIO_14D)
        | (df['previsao_chuva_d1'] > RISK_ALTO_PREVISAO_D1),
        (df['precipitacao_acumulada_3d'] > RISK_MODERADO_PRECIP_ACC_3D)
        | (df['subida_rio_14d'] > RISK_MODERADO_SUBIDA_RIO_14D)
        | (df['previsao_chuva_d1'] > RISK_MODERADO_PREVISAO_D1),
    ]
    choices = [2, 1]
    return np.select(conditions, choices, default=0)


def ensure_feature_columns(df: pd.DataFrame, features=FEATURES) -> pd.DataFrame:
    """Garante que todas as colunas de `features` existam no DataFrame,
    preenchendo com 0 as que estiverem faltando (ex.: previsão indisponível)."""
    df = df.copy()
    for col in features:
        if col not in df:
            df[col] = 0
    return df
