from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class BaseConnector(ABC):
    """
    Classe base abstrata para todos os conectores de fontes de dados.
    Define a interface que cada conector deve implementar.
    """

    @abstractmethod
    def get_data(self, station_id: str, **kwargs: Any) -> pd.DataFrame:
        """
        Método principal para buscar dados de uma estação específica.

        Args:
            station_id (str): O identificador único da estação a ser consultada.
            **kwargs: Argumentos adicionais como datas de início/fim, etc.

        Returns:
            pd.DataFrame: Um DataFrame do Pandas contendo os dados, que devem
                          incluir uma coluna 'data' para facilitar a junção.
        """
        pass
