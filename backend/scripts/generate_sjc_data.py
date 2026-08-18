"""
Gera/atualiza os datasets históricos das 6 regiões administrativas de São
José dos Campos (SP) com dados REAIS, cobrindo a estação chuvosa mais
recente já concluída (dez-fev, quando o clima Cwa da região concentra a
maior parte da precipitação anual e a imprensa local mais reporta
alagamentos na cidade).

Histórico da decisão (18/08/2026): até esta versão, os dados eram
inteiramente sintéticos (gerados por simulação estatística). Ao integrar
fontes reais, descobrimos que:
  - a API pública do INMET (apitempo.inmet.gov.br) tem o endpoint de dados
    fora do ar na prática (retorna vazio para qualquer estação/período);
  - a Open-Meteo Archive API dá precipitação diária REAL (ERA5) por
    coordenada, sem autenticação — usada aqui no lugar do INMET;
  - a ANA tem uma única estação telemétrica real dentro do município
    (58128200, Rio Jaguari) — usada aqui, com a mesma calibração
    real+exposição regional do `backend/connectors/ana_connector.py`
    (não fingimos 6 estações reais independentes).

Estes datasets continuam servindo dois papéis: (1) base para o treino do
modelo (`backend/model.py`) e (2) fallback offline dos conectores reais
(`backend/connectors/precipitation_connector.py` e `ana_connector.py`)
quando as APIs estiverem indisponíveis. Ver IMPLEMENTATION_PLAN.md e
CASE_STUDY_SJC.md para o racional completo.

Uso:
    python -m backend.scripts.generate_sjc_data
"""
import io
import os
from datetime import date

import httpx
import pandas as pd

from backend.connectors.ana_connector import (
    REAL_STATION_CODE,
    REGION_EXPOSURE_FACTOR,
    REGION_RIVER_BASELINE_M,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "historical_data")

REGION_COORDS = {
    "centro":   (-23.1794, -45.8869),
    "norte":    (-23.1300, -45.8900),
    "sul":      (-23.2300, -45.8900),
    "leste":    (-23.1900, -45.8100),
    "oeste":    (-23.1900, -45.9500),
    "sudeste":  (-23.2300, -45.8100),
}

ARCHIVE_API_URL = "https://archive-api.open-meteo.com/v1/archive"
ANA_API_URL = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos"


def _most_recent_rainy_season() -> tuple[date, date]:
    """
    Retorna (início, fim) da estação chuvosa (dez-fev) mais recente já
    CONCLUÍDA em relação a hoje — evita treinar com uma estação parcial.
    """
    today = date.today()
    # Fim de fevereiro do ano corrente (ou do ano passado, se ainda não
    # chegamos lá) marca o fim da última estação concluída.
    end_year = today.year if today.month > 2 or (today.month == 2 and today.day >= 28) else today.year - 1
    end = date(end_year, 2, 28)
    start = date(end_year - 1, 12, 1)
    return start, end


def fetch_precipitation(lat: float, lon: float, start: date, end: date) -> pd.DataFrame:
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "daily": "precipitation_sum", "timezone": "America/Sao_Paulo",
    }
    with httpx.Client(timeout=20.0) as client:
        response = client.get(ARCHIVE_API_URL, params=params)
        response.raise_for_status()
        payload = response.json()
    daily = payload.get("daily", {})
    return pd.DataFrame({
        "data": pd.to_datetime(daily.get("time", [])),
        "precipitacao_mm": daily.get("precipitation_sum", []),
    })


def fetch_real_station_level(start: date, end: date) -> pd.DataFrame:
    params = {
        "codEstacao": REAL_STATION_CODE,
        "dataInicio": start.strftime("%d/%m/%Y"),
        "dataFim": end.strftime("%d/%m/%Y"),
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.get(ANA_API_URL, params=params)
        response.raise_for_status()
        df = pd.read_xml(io.StringIO(response.text), xpath=".//DadosHidrometereologicos", parser="etree")

    df["data"] = pd.to_datetime(df["DataHora"].astype(str).str.strip()).dt.normalize()
    df["nivel_estacao_m"] = pd.to_numeric(df["Nivel"], errors="coerce") / 100.0
    return df.dropna(subset=["nivel_estacao_m"]).groupby("data", as_index=False)["nivel_estacao_m"].mean()


def derive_regional_level(station_daily: pd.DataFrame, region_id: str) -> pd.DataFrame:
    baseline = REGION_RIVER_BASELINE_M.get(region_id, REGION_RIVER_BASELINE_M["centro"])
    exposure = REGION_EXPOSURE_FACTOR.get(region_id, 1.0)
    station_mean = station_daily["nivel_estacao_m"].mean()
    anomalia = (station_daily["nivel_estacao_m"] - station_mean) * 0.15
    return pd.DataFrame({
        "data": station_daily["data"],
        "nivel_rio_m": (baseline + exposure * anomalia).round(2),
    })


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start, end = _most_recent_rainy_season()
    print(f"INFO: buscando dados reais de {start} a {end} (estação chuvosa mais recente concluída)")

    print("INFO: buscando nível real da estação ANA 58128200 (Rio Jaguari, SJC)...")
    station_daily = fetch_real_station_level(start, end)
    print(f"INFO: {len(station_daily)} dias de nível real obtidos.")

    for region_id, (lat, lon) in REGION_COORDS.items():
        precip_df = fetch_precipitation(lat, lon, start, end)
        river_df = derive_regional_level(station_daily, region_id)

        df = pd.merge(precip_df, river_df, on="data", how="inner").sort_values("data").reset_index(drop=True)
        out_path = os.path.join(OUTPUT_DIR, f"{region_id}.csv")
        df.to_csv(out_path, index=False)
        print(f"INFO: gerado {out_path} ({len(df)} dias, chuva total {df['precipitacao_mm'].sum():.1f}mm, "
              f"nível máx {df['nivel_rio_m'].max():.2f}m)")

    print("\nOK: datasets históricos REAIS de São José dos Campos gerados em backend/historical_data/")
    print("Fontes: Open-Meteo Archive (precipitação) + ANA estação 58128200 (nível, com calibração regional).")


if __name__ == "__main__":
    main()
