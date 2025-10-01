"""
Modelo predictivo para anticipar demanda ciudadana.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import yaml
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DemandPredictor:
    """Modelo predictivo para anticipar demanda ciudadana."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Inicializa el predictor de demanda.
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.model_config = self.config['model']
        self.models_dir = Path(self.model_config['models_dir'])
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Modelos
        self.rf_model = None
        self.gb_model = None
        self.ensemble_model = None
        
        # Encoders para variables categóricas
        self.label_encoders = {}
        
        # Datos
        self.data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
    
    def load_data(self, data_path: str = None) -> pd.DataFrame:
        """
        Carga los datos para entrenamiento.
        
        Args:
            data_path: Ruta al archivo de datos
            
        Returns:
            DataFrame con los datos cargados
        """
        if data_path is None:
            data_path = Path(self.config['etl']['processed_data_dir']) / 'consolidated_latest.csv'
        
        self.data = pd.read_csv(data_path)
        self.data['fecha_solicitud'] = pd.to_datetime(self.data['fecha_solicitud'])
        self.data['fecha_resolucion'] = pd.to_datetime(self.data['fecha_resolucion'])
        
        logger.info(f"Datos cargados: {len(self.data)} registros")
        return self.data
    
    def prepare_features(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Prepara las características para el modelo.
        
        Args:
            df: DataFrame con los datos. Si es None, usa self.data
            
        Returns:
            DataFrame con características preparadas
        """
        if df is None:
            df = self.data.copy()
        else:
            df = df.copy()
        
        # Extraer características temporales
        df['anio'] = df['fecha_solicitud'].dt.year
        df['mes'] = df['fecha_solicitud'].dt.month
        df['dia'] = df['fecha_solicitud'].dt.day
        df['dia_semana'] = df['fecha_solicitud'].dt.dayofweek
        df['hora'] = df['fecha_solicitud'].dt.hour
        df['trimestre'] = df['fecha_solicitud'].dt.quarter
        df['dia_del_anio'] = df['fecha_solicitud'].dt.dayofyear
        df['semana_del_anio'] = df['fecha_solicitud'].dt.isocalendar().week
        
        # Características de ventana temporal (últimos 7, 14, 30 días)
        df = df.sort_values('fecha_solicitud')
        df['solicitudes_ultimos_7d'] = df.groupby('categoria')['solicitud_id'].transform(
            lambda x: x.rolling(window=7, min_periods=1).count()
        )
        df['solicitudes_ultimos_14d'] = df.groupby('categoria')['solicitud_id'].transform(
            lambda x: x.rolling(window=14, min_periods=1).count()
        )
        df['solicitudes_ultimos_30d'] = df.groupby('categoria')['solicitud_id'].transform(
            lambda x: x.rolling(window=30, min_periods=1).count()
        )
        
        # Codificar variables categóricas
        categorical_columns = ['categoria', 'estado', 'fuente']
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Para datos nuevos, usar el encoder ya entrenado
                    df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        logger.info(f"Características preparadas: {len(df.columns)} columnas")
        return df
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara los datos para entrenamiento.
        
        Returns:
            Tupla (X, y) con características y variable objetivo
        """
        df = self.prepare_features()
        
        # Variable objetivo: tiempo de atención
        # Filtrar solo registros con tiempo de atención conocido
        df = df[df['tiempo_atencion_horas'].notna()].copy()
        
        # Características para el modelo
        feature_columns = [
            'anio', 'mes', 'dia', 'dia_semana', 'hora', 'trimestre',
            'dia_del_anio', 'semana_del_anio',
            'solicitudes_ultimos_7d', 'solicitudes_ultimos_14d', 'solicitudes_ultimos_30d',
            'categoria_encoded', 'estado_encoded', 'fuente_encoded'
        ]
        
        # Filtrar columnas disponibles
        available_features = [col for col in feature_columns if col in df.columns]
        
        X = df[available_features]
        y = df['tiempo_atencion_horas']
        
        logger.info(f"Datos de entrenamiento preparados: {len(X)} muestras, {len(available_features)} características")
        return X, y
    
    def train(self, test_size: float = 0.2) -> Dict:
        """
        Entrena el modelo predictivo.
        
        Args:
            test_size: Proporción de datos para prueba
            
        Returns:
            Diccionario con métricas de evaluación
        """
        logger.info("Iniciando entrenamiento del modelo...")
        
        # Preparar datos
        X, y = self.prepare_training_data()
        
        # Dividir en entrenamiento y prueba
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.model_config['parameters']['random_state']
        )
        
        # Entrenar Random Forest
        logger.info("Entrenando Random Forest...")
        self.rf_model = RandomForestRegressor(
            n_estimators=self.model_config['parameters']['n_estimators'],
            max_depth=self.model_config['parameters']['max_depth'],
            random_state=self.model_config['parameters']['random_state'],
            n_jobs=-1
        )
        self.rf_model.fit(self.X_train, self.y_train)
        
        # Entrenar Gradient Boosting
        logger.info("Entrenando Gradient Boosting...")
        self.gb_model = GradientBoostingRegressor(
            n_estimators=self.model_config['parameters']['n_estimators'],
            max_depth=self.model_config['parameters']['max_depth'],
            learning_rate=self.model_config['parameters']['learning_rate'],
            random_state=self.model_config['parameters']['random_state']
        )
        self.gb_model.fit(self.X_train, self.y_train)
        
        # Evaluación
        metrics = self.evaluate()
        
        # Guardar modelos
        self.save_models()
        
        logger.info("Entrenamiento completado")
        return metrics
    
    def evaluate(self) -> Dict:
        """
        Evalúa los modelos entrenados.
        
        Returns:
            Diccionario con métricas de evaluación
        """
        metrics = {}
        
        # Predicciones Random Forest
        y_pred_rf = self.rf_model.predict(self.X_test)
        metrics['random_forest'] = {
            'rmse': np.sqrt(mean_squared_error(self.y_test, y_pred_rf)),
            'mae': mean_absolute_error(self.y_test, y_pred_rf),
            'r2': r2_score(self.y_test, y_pred_rf)
        }
        
        # Predicciones Gradient Boosting
        y_pred_gb = self.gb_model.predict(self.X_test)
        metrics['gradient_boosting'] = {
            'rmse': np.sqrt(mean_squared_error(self.y_test, y_pred_gb)),
            'mae': mean_absolute_error(self.y_test, y_pred_gb),
            'r2': r2_score(self.y_test, y_pred_gb)
        }
        
        # Ensemble (promedio de ambos modelos)
        y_pred_ensemble = (y_pred_rf + y_pred_gb) / 2
        metrics['ensemble'] = {
            'rmse': np.sqrt(mean_squared_error(self.y_test, y_pred_ensemble)),
            'mae': mean_absolute_error(self.y_test, y_pred_ensemble),
            'r2': r2_score(self.y_test, y_pred_ensemble)
        }
        
        # Importancia de características (Random Forest)
        feature_importance = pd.DataFrame({
            'feature': self.X_train.columns,
            'importance': self.rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        metrics['feature_importance'] = feature_importance.to_dict('records')
        
        logger.info(f"Métricas - Ensemble RMSE: {metrics['ensemble']['rmse']:.2f}, "
                   f"MAE: {metrics['ensemble']['mae']:.2f}, R²: {metrics['ensemble']['r2']:.3f}")
        
        return metrics
    
    def predict_demand(self, days_ahead: int = 30) -> pd.DataFrame:
        """
        Predice la demanda para los próximos días.
        
        Args:
            days_ahead: Número de días a predecir
            
        Returns:
            DataFrame con las predicciones
        """
        logger.info(f"Generando predicciones para {days_ahead} días...")
        
        # Generar fechas futuras
        last_date = self.data['fecha_solicitud'].max()
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=days_ahead,
            freq='D'
        )
        
        # Crear DataFrame con fechas futuras
        predictions = []
        
        for date in future_dates:
            for categoria in self.data['categoria'].unique():
                # Crear registro para predicción
                record = pd.DataFrame({
                    'fecha_solicitud': [date],
                    'categoria': [categoria],
                    'estado': ['Pendiente'],
                    'fuente': ['db1']
                })
                
                # Preparar características
                record_features = self.prepare_features(record)
                
                # Seleccionar las mismas características usadas en entrenamiento
                X_pred = record_features[self.X_train.columns]
                
                # Predecir con ambos modelos
                pred_rf = self.rf_model.predict(X_pred)[0]
                pred_gb = self.gb_model.predict(X_pred)[0]
                pred_ensemble = (pred_rf + pred_gb) / 2
                
                predictions.append({
                    'fecha': date,
                    'categoria': categoria,
                    'tiempo_atencion_predicho': pred_ensemble,
                    'prediccion_rf': pred_rf,
                    'prediccion_gb': pred_gb
                })
        
        predictions_df = pd.DataFrame(predictions)
        logger.info(f"Predicciones generadas: {len(predictions_df)} registros")
        
        return predictions_df
    
    def save_models(self) -> None:
        """Guarda los modelos entrenados."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar Random Forest
        rf_path = self.models_dir / f'random_forest_{timestamp}.joblib'
        joblib.dump(self.rf_model, rf_path)
        logger.info(f"Random Forest guardado en {rf_path}")
        
        # Guardar Gradient Boosting
        gb_path = self.models_dir / f'gradient_boosting_{timestamp}.joblib'
        joblib.dump(self.gb_model, gb_path)
        logger.info(f"Gradient Boosting guardado en {gb_path}")
        
        # Guardar encoders
        encoders_path = self.models_dir / f'label_encoders_{timestamp}.joblib'
        joblib.dump(self.label_encoders, encoders_path)
        logger.info(f"Label encoders guardados en {encoders_path}")
        
        # Guardar referencia al último modelo
        joblib.dump(self.rf_model, self.models_dir / 'random_forest_latest.joblib')
        joblib.dump(self.gb_model, self.models_dir / 'gradient_boosting_latest.joblib')
        joblib.dump(self.label_encoders, self.models_dir / 'label_encoders_latest.joblib')
    
    def load_models(self, timestamp: str = 'latest') -> None:
        """
        Carga modelos previamente entrenados.
        
        Args:
            timestamp: Timestamp del modelo a cargar, o 'latest' para el más reciente
        """
        rf_path = self.models_dir / f'random_forest_{timestamp}.joblib'
        gb_path = self.models_dir / f'gradient_boosting_{timestamp}.joblib'
        encoders_path = self.models_dir / f'label_encoders_{timestamp}.joblib'
        
        self.rf_model = joblib.load(rf_path)
        self.gb_model = joblib.load(gb_path)
        self.label_encoders = joblib.load(encoders_path)
        
        logger.info(f"Modelos cargados desde {timestamp}")


def main():
    """Función principal para entrenar el modelo."""
    try:
        predictor = DemandPredictor()
        predictor.load_data()
        
        # Entrenar modelo
        metrics = predictor.train()
        
        # Guardar métricas
        metrics_path = Path('reports/generated') / f"model_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metrics_path, 'w') as f:
            yaml.dump(metrics, f, default_flow_style=False)
        
        print(f"Modelo entrenado exitosamente. Métricas guardadas en: {metrics_path}")
        
        # Generar predicciones de ejemplo
        predictions = predictor.predict_demand(days_ahead=30)
        pred_path = Path('reports/generated') / f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        predictions.to_csv(pred_path, index=False)
        print(f"Predicciones guardadas en: {pred_path}")
        
    except Exception as e:
        logger.error(f"Error al entrenar modelo: {str(e)}")
        raise


if __name__ == "__main__":
    main()
