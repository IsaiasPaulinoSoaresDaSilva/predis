import pandas as pd
import httpx
from typing import Any, Dict
from backend.connectors.base_connector import BaseConnector

class OpenMeteoConnector(BaseConnector):
    """
    Conector para buscar dados de previsão do tempo da API Open-Meteo.
    """
    API_URL = "https://api.open-meteo.com/v1/forecast"

    def get_data(self, station_id: str = None, **kwargs: Any) -> pd.DataFrame:
        """
        Busca dados de previsão de precipitação para uma determinada latitude e longitude.

        Args:
            station_id (str): Ignorado. A busca é por lat/lon.
            **kwargs: Deve conter 'latitude' e 'longitude'.

        Returns:
            pd.DataFrame: DataFrame com a previsão de chuva para os próximos dias.
                          As colunas são renomeadas para 'previsao_chuva_d1', 'd2', etc.
        """
        latitude = kwargs.get('latitude')
        longitude = kwargs.get('longitude')

        if not latitude or not longitude:
            raise ValueError("Latitude e Longitude são necessárias para o OpenMeteoConnector.")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "precipitation_sum",
            "forecast_days": 3, # Buscando previsão para os próximos 3 dias
            "timezone": "auto"
        }

        try:
            with httpx.Client() as client:
                response = client.get(self.API_URL, params=params)
                response.raise_for_status() # Lança um erro para status HTTP 4xx/5xx
                data = response.json()

            # Processar a resposta da API
            daily_data = data['daily']
            df = pd.DataFrame(daily_data)
            df.rename(columns={'time': 'data', 'precipitation_sum': 'previsao_chuva_mm'}, inplace=True)
            
            # Converter a data para o mesmo formato dos outros conectores
            df['data'] = pd.to_datetime(df['data'])
            
            # Pivotar o DataFrame para ter previsões em colunas (d+1, d+2, d+3)
            # Esta lógica é um pouco mais complexa, pois a API retorna em linhas.
            # Para o nosso modelo, é mais fácil ter colunas de features.
            # Por simplicidade aqui, vamos apenas retornar os dados como estão
            # e a lógica de engenharia de features no `model.py` irá processá-los.
            print(f"INFO: [OpenMeteoConnector] Dados de previsão obtidos para Lat: {latitude}, Lon: {longitude}")
            return df

        except httpx.HTTPStatusError as e:
            print(f"ERRO: [OpenMeteoConnector] Erro na API Open-Meteo: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"ERRO: [OpenMeteoConnector] Erro inesperado: {e}")
            return pd.DataFrame()

# Exemplo de uso (para teste)
if __name__ == '__main__':
    # Coordenadas de São Paulo (exemplo)
    connector = OpenMeteoConnector()
    forecast = connector.get_data(latitude=-23.55, longitude=-46.63)
    if not forecast.empty:
        print("\nPrevisão de chuva para os próximos 3 dias:")
        print(forecast)
