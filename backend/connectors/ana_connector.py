"""
Conector de nível de rio REAL para o estudo de caso de São José dos Campos,
via ServiceANA (webservice legado de telemetria da Agência Nacional de
Águas, `telemetriaws1.ana.gov.br`) — funciona sem autenticação (ao contrário
do HidroWebService novo, que exige token OAuth).

Descoberta da integração (18/08/2026): consultamos o inventário de estações
da ANA (`HidroInventario`) por faixa de código na bacia do Paraíba do Sul e
achamos uma estação telemétrica REAL fisicamente dentro de São José dos
Campos: código 58128200 ("UHE Jaguari Jusante", Rio Jaguari), com dados
horários reais de nível/vazão/chuva desde 2012, confirmados via a chamada
`DadosHidrometeorologicos`.

Limitação importante, documentada de propósito: é a ÚNICA estação
telemétrica real dentro do município — não existem estações telemétricas
públicas por bairro/região. Além disso, é uma estação de barragem
(hidrelétrica), então seu nível é influenciado pela operação do
reservatório, não é um rio natural "puro". Por isso, não fingimos 6 medições
reais independentes: usamos a ANOMALIA do nível real dessa estação (desvio
da própria média móvel recente) como sinal hidrológico real comum às 6
regiões, escalado pelo fator de exposição a enchente já documentado
publicamente por região (ver `backend/scripts/generate_sjc_data.py` e
CASE_STUDY_SJC.md) — ou seja: "sinal real + calibração regional
transparente", nunca "6 estações reais".
"""
import io
import os
import time
from datetime import date, timedelta
from typing import Any, Dict, Tuple

import httpx
import pandas as pd

from backend.connectors.base_connector import BaseConnector

HISTORICAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "historical_data")

# Única estação telemétrica real da ANA dentro de São José dos Campos
# (achada via HidroInventario, ver docstring acima).
REAL_STATION_CODE = "58128200"  # UHE Jaguari Jusante, Rio Jaguari

# Baseline de referência (nível "seco" típico, em metros — nivel_rio_m já
# usado no restante do app) e fator de exposição a enchente por região,
# herdados da calibração pública documentada em generate_sjc_data.py /
# CASE_STUDY_SJC.md (Sul/Leste mais expostas, Norte/Oeste menos).
REGION_RIVER_BASELINE_M = {
    "centro": 2.0, "norte": 1.5, "sul": 1.8,
    "leste": 2.2, "oeste": 1.4, "sudeste": 1.6,
}
REGION_EXPOSURE_FACTOR = {
    "centro": 1.0, "norte": 0.7, "sul": 1.3,
    "leste": 1.4, "oeste": 0.6, "sudeste": 0.9,
}


class ANAConnector(BaseConnector):
    """
    Busca o nível REAL da estação telemétrica da ANA em SJC e deriva uma
    série de "nível de rio" por região a partir da anomalia desse sinal
    real, com cache em memória (TTL) e fallback gracioso para o CSV local
    (`backend/historical_data/<região>.csv`) se a API estiver indisponível.
    """

    SOAP_BASE_URL = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos"
    CACHE_TTL_SECONDS = 1800  # 30 minutos
    LIVE_WINDOW_DAYS = 20

    def __init__(self):
        self._cache: Tuple[float, pd.DataFrame] | None = None

    def get_data(self, station_id: str, **kwargs: Any) -> pd.DataFrame:
        """
        Args:
            station_id (str): identificador da região do estudo de caso
                (usado para o fallback em CSV e para escalar a anomalia
                real pelo fator de exposição da região).
            **kwargs: ignorados (a estação real é fixa — ver `REAL_STATION_CODE`).

        Returns:
            pd.DataFrame com colunas 'data' e 'nivel_rio_m'.
        """
        base_df = self._load_csv_fallback(station_id)

        live_df = self._fetch_live_regional_level(station_id)
        if live_df is None or live_df.empty:
            return base_df

        combined = pd.concat([base_df, live_df], ignore_index=True)
        combined = combined.drop_duplicates(subset='data', keep='last').sort_values('data').reset_index(drop=True)
        return combined

    def _load_csv_fallback(self, station_id: str) -> pd.DataFrame:
        csv_path = os.path.join(HISTORICAL_DATA_DIR, f"{station_id}.csv")
        try:
            df = pd.read_csv(csv_path, parse_dates=['data'])
            return df[['data', 'nivel_rio_m']]
        except FileNotFoundError:
            print(f"ERRO: [ANAConnector] Arquivo '{csv_path}' não encontrado.")
            return pd.DataFrame({'data': [], 'nivel_rio_m': []})

    def _fetch_live_regional_level(self, region_id: str) -> pd.DataFrame | None:
        raw = self._fetch_real_station_daily()
        if raw is None or raw.empty:
            return None

        baseline = REGION_RIVER_BASELINE_M.get(region_id, REGION_RIVER_BASELINE_M["centro"])
        exposure = REGION_EXPOSURE_FACTOR.get(region_id, 1.0)

        # Anomalia do sinal real: desvio (em metros) da própria média do
        # período buscado, escalado por um ganho pequeno (a estação é uma
        # barragem — variações de dezenas de cm no reservatório não devem
        # virar variações de dezenas de metros no "rio" da região).
        station_mean = raw['nivel_estacao_m'].mean()
        anomalia = (raw['nivel_estacao_m'] - station_mean) * 0.15

        df = pd.DataFrame({
            'data': raw['data'],
            'nivel_rio_m': (baseline + exposure * anomalia).round(2),
        })
        return df

    def _fetch_real_station_daily(self) -> pd.DataFrame | None:
        if self._cache is not None:
            cached_at, cached_df = self._cache
            if time.monotonic() - cached_at < self.CACHE_TTL_SECONDS:
                return cached_df.copy()

        end = date.today()
        start = end - timedelta(days=self.LIVE_WINDOW_DAYS)
        params = {
            "codEstacao": REAL_STATION_CODE,
            "dataInicio": start.strftime("%d/%m/%Y"),
            "dataFim": end.strftime("%d/%m/%Y"),
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(self.SOAP_BASE_URL, params=params)
                response.raise_for_status()
                df = pd.read_xml(io.StringIO(response.text), xpath=".//DadosHidrometereologicos", parser="etree")

            if df.empty or 'Nivel' not in df.columns:
                print("ERRO: [ANAConnector] Resposta da ANA sem dados de nível.")
                return None

            df['data'] = pd.to_datetime(df['DataHora'].astype(str).str.strip()).dt.normalize()
            df['nivel_estacao_m'] = pd.to_numeric(df['Nivel'], errors='coerce') / 100.0
            daily = df.dropna(subset=['nivel_estacao_m']).groupby('data', as_index=False)['nivel_estacao_m'].mean()

            print(f"INFO: [ANAConnector] Dados reais (estação ANA {REAL_STATION_CODE}) "
                  f"obtidos: {len(daily)} dias.")
            self._cache = (time.monotonic(), daily)
            return daily.copy()
        except httpx.HTTPStatusError as e:
            print(f"ERRO: [ANAConnector] Erro na API da ANA: {e}")
            return None
        except httpx.RequestError as e:
            print(f"ERRO: [ANAConnector] Falha de rede na API da ANA: {e}")
            return None
        except Exception as e:
            print(f"ERRO: [ANAConnector] Erro inesperado: {e}")
            return None
