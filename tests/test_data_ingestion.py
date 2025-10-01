"""
Tests para el módulo de ingesta de datos.
"""

import pytest
import pandas as pd
from src.data_ingestion.connector_factory import ConnectorFactory
from src.data_ingestion.base_connector import BaseConnector


def test_connector_factory_postgresql():
    """Test de creación de conector PostgreSQL."""
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'test_db',
        'username': 'test_user',
        'password': 'test_pass',
        'schema': 'public'
    }
    
    connector = ConnectorFactory.create_connector('postgresql', config)
    assert connector is not None
    assert isinstance(connector, BaseConnector)


def test_connector_factory_mysql():
    """Test de creación de conector MySQL."""
    config = {
        'host': 'localhost',
        'port': 3306,
        'database': 'test_db',
        'username': 'test_user',
        'password': 'test_pass'
    }
    
    connector = ConnectorFactory.create_connector('mysql', config)
    assert connector is not None
    assert isinstance(connector, BaseConnector)


def test_connector_factory_sqlserver():
    """Test de creación de conector SQL Server."""
    config = {
        'host': 'localhost',
        'port': 1433,
        'database': 'test_db',
        'username': 'test_user',
        'password': 'test_pass'
    }
    
    connector = ConnectorFactory.create_connector('sqlserver', config)
    assert connector is not None
    assert isinstance(connector, BaseConnector)


def test_connector_factory_invalid_type():
    """Test de manejo de tipo de base de datos inválido."""
    config = {
        'host': 'localhost',
        'database': 'test_db',
        'username': 'test_user',
        'password': 'test_pass'
    }
    
    with pytest.raises(ValueError):
        ConnectorFactory.create_connector('invalid_db', config)
