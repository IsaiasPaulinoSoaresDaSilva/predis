import sys
from pathlib import Path

import pandas as pd
import pytest

# Garante que a raiz do projeto está no sys.path ao rodar `pytest` a partir
# de qualquer diretório (os módulos usam imports absolutos `backend.xxx`).
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture
def fake_forecast_df():
    """Um DataFrame de previsão plausível, no formato retornado pelo
    OpenMeteoConnector real, para usar como stub nos testes (evita
    depender de rede)."""
    return pd.DataFrame({
        'data': pd.to_datetime(['2024-03-01', '2024-03-02', '2024-03-03']),
        'previsao_chuva_mm': [0.0, 5.2, 12.0],
    })


@pytest.fixture(autouse=True)
def no_network_openmeteo(monkeypatch, fake_forecast_df):
    """Por padrão, TODOS os testes usam um stub do OpenMeteoConnector — sem
    isso, a suíte dependeria de rede/da API pública estar no ar."""
    from backend.connectors.openmeteo_connector import OpenMeteoConnector

    def _fake_get_data(self, station_id=None, **kwargs):
        return fake_forecast_df.copy()

    monkeypatch.setattr(OpenMeteoConnector, "get_data", _fake_get_data)


@pytest.fixture(autouse=True)
def no_network_real_data_connectors(monkeypatch):
    """Por padrão, os conectores de precipitação (Open-Meteo Archive) e
    nível de rio (ANA) não tentam rede nos testes — caem direto no fallback
    do CSV local, que é determinístico e rápido. Testes específicos que
    querem exercitar o caminho "ao vivo" reativam a rede monkeypatchando de
    volta ou chamando os métodos internos diretamente com um stub próprio."""
    from backend.connectors.ana_connector import ANAConnector
    from backend.connectors.precipitation_connector import PrecipitationConnector

    monkeypatch.setattr(PrecipitationConnector, "_fetch_live", lambda self, lat, lon: None)
    monkeypatch.setattr(ANAConnector, "_fetch_real_station_daily", lambda self: None)
