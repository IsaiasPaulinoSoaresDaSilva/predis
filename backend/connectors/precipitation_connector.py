"""
Conector de precipitação real para o estudo de caso de São José dos Campos.

Histórico da decisão (18/08/2026): esta classe se chamava `INMETConnector` e
lia um CSV sintético local, simulando uma chamada à API pública do INMET.
Ao integrar dados reais, testamos a API pública do INMET
(`apitempo.inmet.gov.br`) na prática: o endpoint de metadados
(`/estacoes/T`) funciona, mas o endpoint de dados por estação
(`/estacao/{inicio}/{fim}/{codigo}`) retornou vazio (HTTP 204) para toda
estação/período testado — inclusive estações operantes fora de SJC. Também
descobrimos que a estação citada no código antigo (A755) não é de São José
dos Campos, e sim de Barueri (e está em pane). A estação automática mais
próxima de SJC de fato é a A728 (Taubaté, ~40km).

Diante da API do INMET indisponível na prática, usamos a Open-Meteo Archive
API (mesmo provedor já usado para a previsão em `openmeteo_connector.py`,
mas seu endpoint de dados HISTÓRICOS reais — não sintéticos): dados diários
de precipitação por coordenada exata (ERA5, sem necessidade de autenticação),
testada e confirmada para as coordenadas de SJC. Cada uma das 6 regiões do
estudo de caso tem coordenadas reais próprias (ver DataManager), então a
diferenciação regional é preservada com dados genuinamente reais por região
— não uma única série repetida.

Ver IMPLEMENTATION_PLAN.md (Fase 7 — dados reais) e CASE_STUDY_SJC.md para o
racional completo.
"""
import os
import time
from datetime import date, timedelta
from typing import Any, Dict, Tuple

import httpx
import pandas as pd

from backend.connectors.base_connector import BaseConnector

HISTORICAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "historical_data")


class PrecipitationConnector(BaseConnector):
    """
    Busca precipitação diária REAL (Open-Meteo Archive, dados históricos
    ERA5) para as coordenadas de uma região do estudo de caso, com cache em
    memória (TTL) e fallback gracioso para o CSV local
    (`backend/historical_data/<região>.csv`) se a API estiver indisponível
    — preservando a demo/offline mesmo sem rede.
    """

    ARCHIVE_API_URL = "https://archive-api.open-meteo.com/v1/archive"
    CACHE_TTL_SECONDS = 1800  # 30 minutos — chuva real não muda a cada poll de 10s do dashboard
    LIVE_WINDOW_DAYS = 20  # janela recente buscada ao vivo, complementa o histórico do CSV

    def __init__(self):
        self._cache: Dict[Tuple[float, float], Tuple[float, pd.DataFrame]] = {}

    def get_data(self, station_id: str, **kwargs: Any) -> pd.DataFrame:
        """
        Args:
            station_id (str): identificador da região (usado só para o
                fallback em CSV — a busca real é por lat/lon).
            **kwargs: espera 'latitude' e 'longitude' (coordenadas reais da
                região, ver DataManager.location_map).

        Returns:
            pd.DataFrame com colunas 'data' e 'precipitacao_mm': histórico
            base do CSV + janela recente real (quando disponível),
            deduplicado por data (a leitura mais recente prevalece).
        """
        base_df = self._load_csv_fallback(station_id)

        latitude = kwargs.get('latitude')
        longitude = kwargs.get('longitude')
        if latitude is None or longitude is None:
            print(f"INFO: [PrecipitationConnector] Sem lat/lon para '{station_id}' — usando só o CSV local.")
            return base_df

        live_df = self._fetch_live(float(latitude), float(longitude))
        if live_df is None or live_df.empty:
            return base_df

        combined = pd.concat([base_df, live_df], ignore_index=True)
        combined = combined.drop_duplicates(subset='data', keep='last').sort_values('data').reset_index(drop=True)
        return combined

    def _load_csv_fallback(self, station_id: str) -> pd.DataFrame:
        csv_path = os.path.join(HISTORICAL_DATA_DIR, f"{station_id}.csv")
        try:
            df = pd.read_csv(csv_path, parse_dates=['data'])
            return df[['data', 'precipitacao_mm']]
        except FileNotFoundError:
            print(f"ERRO: [PrecipitationConnector] Arquivo '{csv_path}' não encontrado.")
            return pd.DataFrame({'data': [], 'precipitacao_mm': []})

    def _fetch_live(self, latitude: float, longitude: float) -> pd.DataFrame | None:
        cache_key = (round(latitude, 3), round(longitude, 3))
        cached = self._cache.get(cache_key)
        if cached is not None:
            cached_at, cached_df = cached
            if time.monotonic() - cached_at < self.CACHE_TTL_SECONDS:
                return cached_df.copy()

        end = date.today()
        start = end - timedelta(days=self.LIVE_WINDOW_DAYS)
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": "precipitation_sum",
            "timezone": "America/Sao_Paulo",
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.ARCHIVE_API_URL, params=params)
                response.raise_for_status()
                payload = response.json()

            daily = payload.get('daily', {})
            df = pd.DataFrame({
                'data': pd.to_datetime(daily.get('time', [])),
                'precipitacao_mm': daily.get('precipitation_sum', []),
            }).dropna(subset=['precipitacao_mm'])

            print(f"INFO: [PrecipitationConnector] Dados reais (Open-Meteo Archive) obtidos "
                  f"para Lat: {latitude}, Lon: {longitude} ({len(df)} dias).")
            self._cache[cache_key] = (time.monotonic(), df)
            return df.copy()
        except httpx.HTTPStatusError as e:
            print(f"ERRO: [PrecipitationConnector] Erro na Open-Meteo Archive: {e}")
            return None
        except httpx.RequestError as e:
            print(f"ERRO: [PrecipitationConnector] Falha de rede na Open-Meteo Archive: {e}")
            return None
        except Exception as e:
            print(f"ERRO: [PrecipitationConnector] Erro inesperado: {e}")
            return None
