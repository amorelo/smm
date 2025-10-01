"""
Factory para crear conectores de bases de datos.
"""

from typing import Dict
import logging

from .connectors import PostgreSQLConnector, MySQLConnector, SQLServerConnector
from .base_connector import BaseConnector

logger = logging.getLogger(__name__)


class ConnectorFactory:
    """Factory para crear instancias de conectores."""
    
    _connectors = {
        'postgresql': PostgreSQLConnector,
        'mysql': MySQLConnector,
        'sqlserver': SQLServerConnector,
    }
    
    @classmethod
    def create_connector(cls, db_type: str, config: Dict) -> BaseConnector:
        """
        Crea un conector según el tipo de base de datos.
        
        Args:
            db_type: Tipo de base de datos (postgresql, mysql, sqlserver)
            config: Configuración de la base de datos
            
        Returns:
            Instancia del conector apropiado
            
        Raises:
            ValueError: Si el tipo de base de datos no es soportado
        """
        connector_class = cls._connectors.get(db_type.lower())
        
        if connector_class is None:
            raise ValueError(
                f"Tipo de base de datos no soportado: {db_type}. "
                f"Tipos disponibles: {', '.join(cls._connectors.keys())}"
            )
        
        logger.info(f"Creando conector para {db_type}")
        return connector_class(config)
    
    @classmethod
    def register_connector(cls, db_type: str, connector_class: type) -> None:
        """
        Registra un nuevo tipo de conector.
        
        Args:
            db_type: Identificador del tipo de base de datos
            connector_class: Clase del conector
        """
        cls._connectors[db_type.lower()] = connector_class
        logger.info(f"Conector registrado: {db_type}")
