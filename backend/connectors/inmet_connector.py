import pandas as pd
from typing import Any
from backend.connectors.base_connector import BaseConnector

class INMETConnector(BaseConnector):
    """
    Conector simulado para dados de precipitação do INMET.
    
    No futuro, este conector conteria a lógica para se conectar a uma API
    real do INMET ou fazer web scraping. Por enquanto, ele lê dados
    de um arquivo CSV local para simular a resposta.
    """

    def get_data(self, station_id: str, **kwargs: Any) -> pd.DataFrame:
        """
        Simula a busca de dados de precipitação para uma estação do INMET.

        Args:
            station_id (str): O ID da estação do INMET (atualmente ignorado na simulação).
            **kwargs: Argumentos adicionais (ignorados na simulação).

        Returns:
            pd.DataFrame: DataFrame com as colunas 'data' e 'precipitacao_mm'.
        """
        print(f"INFO: [INMETConnector] Simulando busca para estação: {station_id}")
        try:
            # Lê o CSV, garantindo que a coluna 'data' seja parseada corretamente
            df = pd.read_csv('backend/historical_data.csv', parse_dates=['data'])
            # Retorna apenas as colunas relevantes para este conector
            return df[['data', 'precipitacao_mm']]
        except FileNotFoundError:
            print(f"ERRO: [INMETConnector] Arquivo 'historical_data.csv' não encontrado.")
            # Retorna um DataFrame vazio em caso de erro
            return pd.DataFrame({'data': [], 'precipitacao_mm': []})

