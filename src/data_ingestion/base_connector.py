"""
Conector base para las bases de datos del sistema.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd


class BaseConnector(ABC):
    """Clase base para conectores de bases de datos."""
    
    def __init__(self, config: Dict):
        """
        Inicializa el conector con la configuración proporcionada.
        
        Args:
            config: Diccionario con la configuración de la base de datos
        """
        self.config = config
        self.connection = None
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establece conexión con la base de datos.
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Cierra la conexión con la base de datos."""
        pass
    
    @abstractmethod
    def extract_data(self, query: str = None) -> pd.DataFrame:
        """
        Extrae datos de la base de datos.
        
        Args:
            query: Query SQL opcional para extracción personalizada
            
        Returns:
            DataFrame con los datos extraídos
        """
        pass
    
    def validate_connection(self) -> bool:
        """
        Valida que la conexión esté activa.
        
        Returns:
            bool: True si la conexión está activa
        """
        return self.connection is not None
    
    def __enter__(self):
        """Permite usar el conector con context manager."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager."""
        self.disconnect()
