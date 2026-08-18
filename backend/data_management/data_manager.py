import pandas as pd
from backend.connectors.precipitation_connector import PrecipitationConnector
from backend.connectors.ana_connector import ANAConnector
from backend.connectors.openmeteo_connector import OpenMeteoConnector
from functools import reduce

class DataManager:
    """
    Orquestra múltiplos conectores de dados para buscar, unir e
    fornecer um conjunto de dados coeso para a aplicação.

    Estudo de caso: São José dos Campos (SP). As regiões abaixo correspondem
    à divisão administrativa real do município (Centro, Norte, Sul, Leste,
    Oeste, Sudeste — ver Prefeitura de SJC / IBGE), cada uma com suas
    coordenadas reais. A precipitação vem da Open-Meteo Archive (real, por
    coordenada — ver `PrecipitationConnector`) e o nível de rio é derivado
    da única estação telemétrica real da ANA dentro do município (ver
    `ANAConnector`), com fallback para `backend/historical_data/<região>.csv`
    se as APIs estiverem indisponíveis. Ver frontend/src/assets/sjc-regions.json
    para o contexto geográfico (bairros de referência e curso d'água) de
    cada região.
    """
    def __init__(self):
        self.connectors = {
            'precipitation': PrecipitationConnector(),
            'ana': ANAConnector(),
            'openmeteo': OpenMeteoConnector(),
        }

        # lat/lon: coordenadas reais (aproximadas ao centro de cada região),
        # usadas tanto pela previsão (Open-Meteo forecast) quanto pelo
        # histórico real de chuva (Open-Meteo Archive).
        # csv_region: identificador usado por AMBOS os conectores para o
        # fallback em CSV local (backend/historical_data/<csv_region>.csv)
        # quando a busca real (Open-Meteo Archive / ANA) falha ou a região
        # é desconhecida — sempre resolvido para uma das 6 regiões reais.
        self.location_map = {
            'centro':   {'csv_region': 'centro',   'lat': -23.1794, 'lon': -45.8869},
            'norte':    {'csv_region': 'norte',    'lat': -23.1300, 'lon': -45.8900},
            'sul':      {'csv_region': 'sul',      'lat': -23.2300, 'lon': -45.8900},
            'leste':    {'csv_region': 'leste',    'lat': -23.1900, 'lon': -45.8100},
            'oeste':    {'csv_region': 'oeste',    'lat': -23.1900, 'lon': -45.9500},
            'sudeste':  {'csv_region': 'sudeste',  'lat': -23.2300, 'lon': -45.8100},
            'default':  {'csv_region': 'centro',   'lat': -23.1794, 'lon': -45.8869},
        }

    def get_combined_data(self, region_id: str) -> pd.DataFrame:
        location_info = self.location_map.get(region_id.lower(), self.location_map['default'])
        csv_region = location_info['csv_region']

        # --- 1. Buscar Dados Históricos ---
        historical_dfs = []
        precip_df = self.connectors['precipitation'].get_data(
            station_id=csv_region, latitude=location_info['lat'], longitude=location_info['lon']
        )
        if not precip_df.empty:
            historical_dfs.append(precip_df)

        ana_df = self.connectors['ana'].get_data(station_id=csv_region)
        if not ana_df.empty:
            historical_dfs.append(ana_df)

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
