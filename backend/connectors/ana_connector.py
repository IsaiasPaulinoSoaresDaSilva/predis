import pandas as pd
from typing import Any
from backend.connectors.base_connector import BaseConnector

class ANAConnector(BaseConnector):
    """
    Conector simulado para dados de nível de rio da Agência Nacional de Águas (ANA).
    
    Assim como o INMETConnector, este simula a busca de dados lendo de um CSV local.
    """

    def get_data(self, station_id: str, **kwargs: Any) -> pd.DataFrame:
        """
        Simula a busca de dados de nível de rio para uma estação da ANA.

        Args:
            station_id (str): O ID da estação da ANA (atualmente ignorado na simulação).
            **kwargs: Argumentos adicionais (ignorados na simulação).

        Returns:
            pd.DataFrame: DataFrame com as colunas 'data' e 'nivel_rio_m'.
        """
        print(f"INFO: [ANAConnector] Simulando busca para estação: {station_id}")
        try:
            df = pd.read_csv('backend/historical_data.csv', parse_dates=['data'])
            # Retorna apenas as colunas relevantes para este conector
            return df[['data', 'nivel_rio_m']]
        except FileNotFoundError:
            print(f"ERRO: [ANAConnector] Arquivo 'historical_data.csv' não encontrado.")
            return pd.DataFrame({'data': [], 'nivel_rio_m': []})

