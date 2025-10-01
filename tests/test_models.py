"""
Tests para el módulo de modelos predictivos.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.models.train_model import DemandPredictor


@pytest.fixture
def sample_training_data():
    """Crea datos de ejemplo para entrenamiento."""
    np.random.seed(42)
    n_samples = 200
    
    dates = pd.date_range(start='2024-01-01', periods=n_samples, freq='D')
    
    data = pd.DataFrame({
        'solicitud_id': range(1, n_samples + 1),
        'fecha_solicitud': dates,
        'fecha_resolucion': dates + pd.to_timedelta(np.random.randint(1, 72, n_samples), unit='h'),
        'categoria': np.random.choice(
            ['Servicios Públicos', 'Infraestructura', 'Seguridad', 'Salud'],
            n_samples
        ),
        'estado': 'Resuelto',
        'tiempo_atencion_horas': np.random.randint(1, 72, n_samples).astype(float),
        'fuente': np.random.choice(['db1', 'db2', 'db3'], n_samples)
    })
    
    return data


def test_prepare_features(sample_training_data):
    """Test de preparación de características."""
    predictor = DemandPredictor.__new__(DemandPredictor)
    predictor.label_encoders = {}
    
    df_features = predictor.prepare_features(sample_training_data)
    
    # Verificar que se crearon las características temporales
    assert 'anio' in df_features.columns
    assert 'mes' in df_features.columns
    assert 'dia_semana' in df_features.columns
    assert 'hora' in df_features.columns
    
    # Verificar que se codificaron las variables categóricas
    assert 'categoria_encoded' in df_features.columns
    assert 'estado_encoded' in df_features.columns
    assert 'fuente_encoded' in df_features.columns


def test_prepare_training_data(sample_training_data, tmp_path):
    """Test de preparación de datos de entrenamiento."""
    predictor = DemandPredictor.__new__(DemandPredictor)
    predictor.label_encoders = {}
    predictor.data = sample_training_data
    
    X, y = predictor.prepare_training_data()
    
    assert len(X) == len(y)
    assert len(X) > 0
    assert y.name == 'tiempo_atencion_horas'
    assert not y.isna().any()


def test_model_training_structure(sample_training_data, tmp_path):
    """Test de estructura de entrenamiento del modelo."""
    # Este test verifica la estructura sin entrenar completamente
    predictor = DemandPredictor.__new__(DemandPredictor)
    predictor.label_encoders = {}
    predictor.data = sample_training_data
    predictor.model_config = {
        'parameters': {
            'n_estimators': 10,  # Reducido para test rápido
            'max_depth': 5,
            'learning_rate': 0.1,
            'random_state': 42
        }
    }
    predictor.models_dir = tmp_path
    
    X, y = predictor.prepare_training_data()
    
    assert X is not None
    assert y is not None
    assert len(X.columns) > 0
