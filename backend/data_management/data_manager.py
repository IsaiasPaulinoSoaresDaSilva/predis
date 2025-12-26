import pandas as pd
from backend.connectors.inmet_connector import INMETConnector
from backend.connectors.ana_connector import ANAConnector
from backend.connectors.openmeteo_connector import OpenMeteoConnector
from functools import reduce

class DataManager:
    """
    Orquestra múltiplos conectores de dados para buscar, unir e
    fornecer um conjunto de dados coeso para a aplicação.
    """
    def __init__(self):
        self.connectors = {
            'inmet': INMETConnector(),
            'ana': ANAConnector(),
            'openmeteo': OpenMeteoConnector(),
        }
        
        self.location_map = {
            'sul': {'inmet_station': 'A801', 'ana_station': '87654321', 'lat': -27.59, 'lon': -48.54},
            'sudeste': {'inmet_station': 'A701', 'ana_station': '12345678', 'lat': -22.90, 'lon': -43.17},
            'centro-oeste': {'inmet_station': 'A901', 'ana_station': '23456789', 'lat': -15.78, 'lon': -47.92},
            'nordeste': {'inmet_station': 'A401', 'ana_station': '34567890', 'lat': -12.97, 'lon': -38.51},
            'norte': {'inmet_station': 'A101', 'ana_station': '45678901', 'lat': -3.11, 'lon': -60.02},
            'default': {'inmet_station': 'DEFAULT', 'ana_station': 'DEFAULT', 'lat': -14.23, 'lon': -51.92},
        }

    def get_combined_data(self, region_id: str) -> pd.DataFrame:
        location_info = self.location_map.get(region_id.lower(), self.location_map['default'])
        
        # --- 1. Buscar Dados Históricos ---
        historical_dfs = []
        for source in ['inmet', 'ana']:
            connector = self.connectors[source]
            station_key = f"{source}_station"
            if station_key in location_info:
                station_id = location_info[station_key]
                df = connector.get_data(station_id=station_id)
                if not df.empty:
                    historical_dfs.append(df)
        
        if not historical_dfs:
            return pd.DataFrame()

        # Une os dados históricos (chuva e rio)
        historical_data = reduce(lambda left, right: pd.merge(left, right, on='data', how='inner'), historical_dfs)

        # --- 2. Buscar Dados de Previsão ---
        forecast_connector = self.connectors['openmeteo']
        forecast_data = forecast_connector.get_data(latitude=location_info['lat'], longitude=location_info['lon'])
        
        if forecast_data.empty:
            # Se a API de previsão falhar, continuamos apenas com os dados históricos
            # e preenchemos as colunas de previsão com 0.
            historical_data['previsao_chuva_d1'] = 0
            historical_data['previsao_chuva_d2'] = 0
            historical_data['previsao_chuva_d3'] = 0
            return historical_data

        # --- 3. Combinar Histórico com Previsão ---
        # Adiciona as colunas de previsão ao dataframe histórico.
        # Esta é uma simplificação para o treinamento: estamos assumindo que a previsão de "hoje"
        # pode ser usada como feature para os dias no passado.
        # Uma implementação mais complexa buscaria previsões passadas.
        forecast_values = forecast_data['previsao_chuva_mm'].values
        historical_data['previsao_chuva_d1'] = forecast_values[0] if len(forecast_values) > 0 else 0
        historical_data['previsao_chuva_d2'] = forecast_values[1] if len(forecast_values) > 1 else 0
        historical_data['previsao_chuva_d3'] = forecast_values[2] if len(forecast_values) > 2 else 0

        return historical_data
