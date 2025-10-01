"""
Tests para el módulo de análisis.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.analysis.kpi_calculator import KPICalculator


@pytest.fixture
def sample_data():
    """Crea datos de ejemplo para pruebas."""
    np.random.seed(42)
    n_samples = 100
    
    dates = pd.date_range(start='2024-01-01', periods=n_samples, freq='D')
    
    data = pd.DataFrame({
        'solicitud_id': range(1, n_samples + 1),
        'fecha_solicitud': dates,
        'fecha_resolucion': dates + pd.to_timedelta(np.random.randint(1, 72, n_samples), unit='h'),
        'categoria': np.random.choice(
            ['Servicios Públicos', 'Infraestructura', 'Seguridad', 'Salud'],
            n_samples
        ),
        'estado': np.random.choice(['Resuelto', 'Pendiente'], n_samples, p=[0.8, 0.2]),
        'tiempo_atencion_horas': np.random.randint(1, 72, n_samples),
        'fuente': np.random.choice(['db1', 'db2', 'db3'], n_samples)
    })
    
    # Dejar algunos pendientes sin fecha de resolución
    mask = data['estado'] == 'Pendiente'
    data.loc[mask, 'fecha_resolucion'] = pd.NaT
    data.loc[mask, 'tiempo_atencion_horas'] = np.nan
    
    return data


def test_kpi_tiempo_promedio_atencion(sample_data, tmp_path):
    """Test del cálculo de tiempo promedio de atención."""
    # Guardar datos temporales
    data_file = tmp_path / "test_data.csv"
    sample_data.to_csv(data_file, index=False)
    
    # Crear calculadora con configuración mínima
    calculator = KPICalculator.__new__(KPICalculator)
    calculator.data = sample_data
    
    kpi = calculator.calculate_tiempo_promedio_atencion()
    
    assert 'nombre' in kpi
    assert 'valor_promedio' in kpi
    assert kpi['valor_promedio'] > 0
    assert 'unidad' in kpi
    assert kpi['unidad'] == 'horas'


def test_kpi_tasa_resolucion(sample_data, tmp_path):
    """Test del cálculo de tasa de resolución."""
    calculator = KPICalculator.__new__(KPICalculator)
    calculator.data = sample_data
    calculator.kpi_config = {'tasa_resolucion_meta': 85}
    
    kpi = calculator.calculate_tasa_resolucion()
    
    assert 'nombre' in kpi
    assert 'valor' in kpi
    assert 0 <= kpi['valor'] <= 100
    assert 'total_solicitudes' in kpi
    assert kpi['total_solicitudes'] == len(sample_data)


def test_kpi_demanda_por_categoria(sample_data):
    """Test del cálculo de demanda por categoría."""
    calculator = KPICalculator.__new__(KPICalculator)
    calculator.data = sample_data
    
    kpi = calculator.calculate_demanda_por_categoria()
    
    assert 'nombre' in kpi
    assert 'distribucion_absoluta' in kpi
    assert 'distribucion_porcentual' in kpi
    assert len(kpi['distribucion_absoluta']) > 0


def test_kpi_tendencias_temporales(sample_data):
    """Test del cálculo de tendencias temporales."""
    calculator = KPICalculator.__new__(KPICalculator)
    calculator.data = sample_data
    
    kpi = calculator.calculate_tendencias_temporales()
    
    assert 'nombre' in kpi
    assert 'demanda_por_dia_semana' in kpi
    assert 'demanda_por_hora' in kpi
    assert 'demanda_por_mes' in kpi
