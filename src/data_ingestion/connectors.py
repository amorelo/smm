"""
Conectores específicos para cada base de datos.
"""

import pandas as pd
from sqlalchemy import create_engine
from typing import Dict
import logging

from .base_connector import BaseConnector

logger = logging.getLogger(__name__)


class PostgreSQLConnector(BaseConnector):
    """Conector para bases de datos PostgreSQL."""
    
    def connect(self) -> bool:
        """Establece conexión con PostgreSQL."""
        try:
            connection_string = (
                f"postgresql://{self.config['username']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
            self.connection = create_engine(connection_string)
            logger.info(f"Conexión exitosa a PostgreSQL: {self.config['database']}")
            return True
        except Exception as e:
            logger.error(f"Error al conectar a PostgreSQL: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión con PostgreSQL."""
        if self.connection:
            self.connection.dispose()
            logger.info("Conexión PostgreSQL cerrada")
    
    def extract_data(self, query: str = None) -> pd.DataFrame:
        """
        Extrae datos de PostgreSQL.
        
        Args:
            query: Query SQL para extracción
            
        Returns:
            DataFrame con los datos
        """
        if query is None:
            query = f"""
                SELECT * FROM {self.config.get('schema', 'public')}.solicitudes
                WHERE fecha_creacion >= CURRENT_DATE - INTERVAL '365 days'
            """
        
        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"Extraídos {len(df)} registros de PostgreSQL")
            return df
        except Exception as e:
            logger.error(f"Error al extraer datos de PostgreSQL: {str(e)}")
            return pd.DataFrame()


class MySQLConnector(BaseConnector):
    """Conector para bases de datos MySQL."""
    
    def connect(self) -> bool:
        """Establece conexión con MySQL."""
        try:
            connection_string = (
                f"mysql+pymysql://{self.config['username']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
            self.connection = create_engine(connection_string)
            logger.info(f"Conexión exitosa a MySQL: {self.config['database']}")
            return True
        except Exception as e:
            logger.error(f"Error al conectar a MySQL: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión con MySQL."""
        if self.connection:
            self.connection.dispose()
            logger.info("Conexión MySQL cerrada")
    
    def extract_data(self, query: str = None) -> pd.DataFrame:
        """
        Extrae datos de MySQL.
        
        Args:
            query: Query SQL para extracción
            
        Returns:
            DataFrame con los datos
        """
        if query is None:
            query = """
                SELECT * FROM atencion_ciudadana
                WHERE fecha_atencion >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
            """
        
        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"Extraídos {len(df)} registros de MySQL")
            return df
        except Exception as e:
            logger.error(f"Error al extraer datos de MySQL: {str(e)}")
            return pd.DataFrame()


class SQLServerConnector(BaseConnector):
    """Conector para bases de datos SQL Server."""
    
    def connect(self) -> bool:
        """Establece conexión con SQL Server."""
        try:
            connection_string = (
                f"mssql+pyodbc://{self.config['username']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
                f"?driver=ODBC+Driver+17+for+SQL+Server"
            )
            self.connection = create_engine(connection_string)
            logger.info(f"Conexión exitosa a SQL Server: {self.config['database']}")
            return True
        except Exception as e:
            logger.error(f"Error al conectar a SQL Server: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión con SQL Server."""
        if self.connection:
            self.connection.dispose()
            logger.info("Conexión SQL Server cerrada")
    
    def extract_data(self, query: str = None) -> pd.DataFrame:
        """
        Extrae datos de SQL Server.
        
        Args:
            query: Query SQL para extracción
            
        Returns:
            DataFrame con los datos
        """
        if query is None:
            query = """
                SELECT * FROM seguimiento
                WHERE fecha_registro >= DATEADD(day, -365, GETDATE())
            """
        
        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"Extraídos {len(df)} registros de SQL Server")
            return df
        except Exception as e:
            logger.error(f"Error al extraer datos de SQL Server: {str(e)}")
            return pd.DataFrame()
