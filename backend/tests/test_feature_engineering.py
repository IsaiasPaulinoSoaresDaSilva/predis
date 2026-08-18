import pandas as pd

from backend.feature_engineering import (
    FEATURES,
    add_rolling_features,
    compute_risk,
    ensure_feature_columns,
)


def _sample_df():
    return pd.DataFrame({
        'data': pd.date_range('2024-01-01', periods=5, freq='D'),
        'precipitacao_mm': [0, 10, 90, 5, 0],
        'nivel_rio_m': [2.0, 2.1, 4.5, 4.3, 4.0],
    })


def test_add_rolling_features_adds_expected_columns():
    df = add_rolling_features(_sample_df())
    for col in ['precipitacao_acumulada_3d', 'precipitacao_max_3d',
                'media_movel_nivel_rio_3d', 'variacao_nivel_rio_1d', 'subida_rio_14d']:
        assert col in df.columns


def test_add_rolling_features_does_not_mutate_input():
    original = _sample_df()
    original_copy = original.copy()
    add_rolling_features(original)
    pd.testing.assert_frame_equal(original, original_copy)


def test_subida_rio_14d_is_rise_above_recent_minimum():
    df = add_rolling_features(_sample_df())
    # No 3º dia (índice 2), a mínima dos últimos 14 dias (aqui, só os dias
    # anteriores disponíveis) é 2.0; nível atual é 4.5 -> subida de 2.5
    assert df.loc[2, 'subida_rio_14d'] == 2.5


def test_precipitacao_acumulada_3d_is_rolling_sum():
    df = add_rolling_features(_sample_df())
    # dia 3 (índice 2): soma dos últimos 3 dias = 0 + 10 + 90
    assert df.loc[2, 'precipitacao_acumulada_3d'] == 100


def test_compute_risk_returns_zero_for_calm_conditions():
    df = pd.DataFrame({
        'precipitacao_acumulada_3d': [0],
        'subida_rio_14d': [0],
        'previsao_chuva_d1': [0],
    })
    assert list(compute_risk(df)) == [0]


def test_compute_risk_returns_alto_when_heavy_rain_and_river_rise():
    df = pd.DataFrame({
        'precipitacao_acumulada_3d': [200],
        'subida_rio_14d': [2.0],
        'previsao_chuva_d1': [0],
    })
    assert list(compute_risk(df)) == [2]


def test_compute_risk_returns_alto_when_forecast_is_extreme_alone():
    # previsao_chuva_d1 > 50 sozinho já classifica como alto risco,
    # independente de precipitação acumulada/nível do rio (ver
    # backend/feature_engineering.py)
    df = pd.DataFrame({
        'precipitacao_acumulada_3d': [0],
        'subida_rio_14d': [0],
        'previsao_chuva_d1': [60],
    })
    assert list(compute_risk(df)) == [2]


def test_compute_risk_returns_moderado_for_intermediate_conditions():
    df = pd.DataFrame({
        'precipitacao_acumulada_3d': [50],
        'subida_rio_14d': [0],
        'previsao_chuva_d1': [0],
    })
    assert list(compute_risk(df)) == [1]


def test_ensure_feature_columns_fills_missing_with_zero():
    df = pd.DataFrame({'precipitacao_mm': [1.0]})
    result = ensure_feature_columns(df, features=FEATURES)
    for col in FEATURES:
        assert col in result.columns
    assert result.loc[0, 'nivel_rio_m'] == 0
