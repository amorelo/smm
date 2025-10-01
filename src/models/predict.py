"""
Script para generar predicciones con el modelo entrenado.
"""

import pandas as pd
import yaml
import logging
from pathlib import Path
from datetime import datetime
from train_model import DemandPredictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_predictions(days_ahead: int = 30):
    """
    Genera predicciones de demanda.
    
    Args:
        days_ahead: Número de días a predecir
    """
    logger.info("Iniciando generación de predicciones...")
    
    # Cargar modelo
    predictor = DemandPredictor()
    predictor.load_models(timestamp='latest')
    
    # Cargar datos
    predictor.load_data()
    
    # Generar predicciones
    predictions = predictor.predict_demand(days_ahead=days_ahead)
    
    # Guardar predicciones
    output_dir = Path('reports/generated')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # CSV
    csv_path = output_dir / f'predictions_{timestamp}.csv'
    predictions.to_csv(csv_path, index=False)
    logger.info(f"Predicciones guardadas en: {csv_path}")
    
    # Excel
    excel_path = output_dir / f'predictions_{timestamp}.xlsx'
    predictions.to_excel(excel_path, index=False)
    logger.info(f"Predicciones guardadas en: {excel_path}")
    
    # Resumen por categoría
    summary = predictions.groupby('categoria').agg({
        'tiempo_atencion_predicho': ['mean', 'std', 'min', 'max']
    }).round(2)
    
    summary_path = output_dir / f'predictions_summary_{timestamp}.yaml'
    with open(summary_path, 'w') as f:
        yaml.dump(summary.to_dict(), f, default_flow_style=False)
    logger.info(f"Resumen guardado en: {summary_path}")
    
    print(f"\nPredicciones generadas exitosamente:")
    print(f"- Archivo detallado: {csv_path}")
    print(f"- Archivo Excel: {excel_path}")
    print(f"- Resumen: {summary_path}")
    print(f"\nTotal de predicciones: {len(predictions)}")
    print(f"Período: {predictions['fecha'].min()} a {predictions['fecha'].max()}")


def main():
    """Función principal."""
    try:
        generate_predictions(days_ahead=30)
    except Exception as e:
        logger.error(f"Error al generar predicciones: {str(e)}")
        raise


if __name__ == "__main__":
    main()
