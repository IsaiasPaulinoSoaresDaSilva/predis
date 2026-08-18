import pandas as pd

from backend.connectors.ana_connector import ANAConnector, REGION_EXPOSURE_FACTOR, REGION_RIVER_BASELINE_M
from backend.connectors.precipitation_connector import PrecipitationConnector

# Os testes abaixo rodam com a rede desligada por padrão (ver
# `no_network_real_data_connectors` em conftest.py) — exercitam o caminho de
# fallback no CSV local, que é o determinístico/rápido para CI. O caminho
# "ao vivo" (API real) é testado à parte, com um stub explícito.


def test_precipitation_connector_falls_back_to_csv_without_network():
    df = PrecipitationConnector().get_data(station_id='centro', latitude=-23.1794, longitude=-45.8869)
    assert not df.empty
    assert list(df.columns) == ['data', 'precipitacao_mm']


def test_ana_connector_falls_back_to_csv_without_network():
    df = ANAConnector().get_data(station_id='leste')
    assert not df.empty
    assert list(df.columns) == ['data', 'nivel_rio_m']


def test_precipitation_connector_returns_empty_df_for_unknown_region():
    df = PrecipitationConnector().get_data(station_id='regiao-que-nao-existe', latitude=-23.1794, longitude=-45.8869)
    assert df.empty


def test_all_sjc_regions_have_historical_data():
    for region_id in ['centro', 'norte', 'sul', 'leste', 'oeste', 'sudeste']:
        precip_df = PrecipitationConnector().get_data(station_id=region_id, latitude=-23.18, longitude=-45.88)
        ana_df = ANAConnector().get_data(station_id=region_id)
        assert not precip_df.empty, f"Sem dados de precipitação para '{region_id}'"
        assert not ana_df.empty, f"Sem dados de nível de rio para '{region_id}'"
        assert len(precip_df) == len(ana_df)


def test_every_region_has_a_baseline_and_exposure_factor():
    # Garante que a calibração regional usada tanto pelo ANAConnector
    # quanto pelo script de geração de dados (generate_sjc_data.py) cobre
    # todas as 6 regiões do estudo de caso.
    for region_id in ['centro', 'norte', 'sul', 'leste', 'oeste', 'sudeste']:
        assert region_id in REGION_RIVER_BASELINE_M
        assert region_id in REGION_EXPOSURE_FACTOR


def test_precipitation_connector_merges_live_data_over_csv(monkeypatch):
    """Exercita o caminho "ao vivo": quando a busca real funciona, o dado
    real deve prevalecer sobre o CSV nas datas em que ambos existem, e datas
    novas (fora do CSV) devem ser incorporadas."""
    connector = PrecipitationConnector()
    base_df = connector._load_csv_fallback('centro')
    last_csv_date = base_df['data'].max()

    fake_live = pd.DataFrame({
        'data': [last_csv_date, last_csv_date + pd.Timedelta(days=1)],
        'precipitacao_mm': [999.0, 1.5],
    })
    monkeypatch.setattr(PrecipitationConnector, "_fetch_live", lambda self, lat, lon: fake_live)

    df = connector.get_data(station_id='centro', latitude=-23.1794, longitude=-45.8869)
    assert df[df['data'] == last_csv_date]['precipitacao_mm'].iloc[0] == 999.0
    assert (df['data'] == last_csv_date + pd.Timedelta(days=1)).any()


def test_ana_connector_derives_higher_level_for_more_exposed_region(monkeypatch):
    """Sul/Leste têm fator de exposição maior que Norte/Oeste — uma mesma
    anomalia real de nível deve se traduzir em variações maiores para as
    regiões mais expostas (ver docstring de ana_connector.py)."""
    fake_station_daily = pd.DataFrame({
        'data': pd.to_datetime(['2026-01-01', '2026-01-02', '2026-01-03']),
        'nivel_estacao_m': [1.70, 1.90, 2.30],  # sobe ao longo dos dias
    })
    monkeypatch.setattr(ANAConnector, "_fetch_real_station_daily", lambda self: fake_station_daily)

    connector = ANAConnector()
    leste_df = connector.get_data(station_id='leste')  # exposição alta (1.4)
    oeste_df = connector.get_data(station_id='oeste')  # exposição baixa (0.6)

    leste_amplitude = leste_df['nivel_rio_m'].max() - leste_df['nivel_rio_m'].min()
    oeste_amplitude = oeste_df['nivel_rio_m'].max() - oeste_df['nivel_rio_m'].min()
    assert leste_amplitude > oeste_amplitude
