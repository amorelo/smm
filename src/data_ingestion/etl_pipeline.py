"""
Pipeline ETL para la extracción, transformación y carga de datos.
"""

import pandas as pd
import yaml
import logging
from pathlib import Path
from typing import Dict, List
import os
from datetime import datetime

from .connector_factory import ConnectorFactory

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Pipeline ETL para consolidar datos de múltiples fuentes."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Inicializa el pipeline ETL.
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        self.raw_data_dir = Path(self.config['etl']['raw_data_dir'])
        self.processed_data_dir = Path(self.config['etl']['processed_data_dir'])
        
        # Crear directorios si no existen
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Carga la configuración desde archivo YAML.
        
        Args:
            config_path: Ruta al archivo de configuración
            
        Returns:
            Diccionario con la configuración
        """
        # Expandir variables de entorno
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for var in ['DB1_USER', 'DB1_PASSWORD', 'DB2_USER', 'DB2_PASSWORD', 
                       'DB3_USER', 'DB3_PASSWORD']:
                content = content.replace(f'${{{var}}}', os.getenv(var, ''))
        
        config = yaml.safe_load(content)
        logger.info(f"Configuración cargada desde {config_path}")
        return config
    
    def extract(self) -> Dict[str, pd.DataFrame]:
        """
        Extrae datos de las tres bases de datos configuradas.
        
        Returns:
            Diccionario con los DataFrames extraídos de cada base de datos
        """
        extracted_data = {}
        
        for db_name, db_config in self.config['databases'].items():
            logger.info(f"Extrayendo datos de {db_name}...")
            
            try:
                connector = ConnectorFactory.create_connector(
                    db_config['type'],
                    db_config
                )
                
                with connector:
                    df = connector.extract_data()
                    extracted_data[db_name] = df
                    
                    # Guardar datos crudos
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = self.raw_data_dir / f"{db_name}_{timestamp}.csv"
                    df.to_csv(filename, index=False)
                    logger.info(f"Datos guardados en {filename}")
                    
            except Exception as e:
                logger.error(f"Error al extraer datos de {db_name}: {str(e)}")
                extracted_data[db_name] = pd.DataFrame()
        
        return extracted_data
    
    def transform(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Transforma y consolida los datos extraídos.
        
        Args:
            data: Diccionario con DataFrames de cada base de datos
            
        Returns:
            DataFrame consolidado y transformado
        """
        logger.info("Iniciando transformación de datos...")
        
        transformed_dfs = []
        
        for db_name, df in data.items():
            if df.empty:
                logger.warning(f"No hay datos para transformar de {db_name}")
                continue
            
            # Estandarizar nombres de columnas
            df_transformed = self._standardize_columns(df, db_name)
            
            # Agregar fuente de datos
            df_transformed['fuente'] = db_name
            
            transformed_dfs.append(df_transformed)
        
        if not transformed_dfs:
            logger.warning("No hay datos para consolidar")
            return pd.DataFrame()
        
        # Consolidar todos los datos
        consolidated_df = pd.concat(transformed_dfs, ignore_index=True)
        
        # Limpiar y normalizar datos
        consolidated_df = self._clean_data(consolidated_df)
        
        logger.info(f"Datos consolidados: {len(consolidated_df)} registros")
        return consolidated_df
    
    def _standardize_columns(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        Estandariza los nombres de columnas según la fuente.
        
        Args:
            df: DataFrame a estandarizar
            source: Fuente de los datos (db1, db2, db3)
            
        Returns:
            DataFrame con columnas estandarizadas
        """
        # Mapeo de columnas según fuente (ajustar según estructura real)
        column_mappings = {
            'db1': {
                'id_solicitud': 'solicitud_id',
                'fecha_creacion': 'fecha_solicitud',
                'fecha_resolucion': 'fecha_resolucion',
                'tipo_solicitud': 'categoria',
                'estado': 'estado',
                'tiempo_atencion': 'tiempo_atencion_horas'
            },
            'db2': {
                'id_atencion': 'solicitud_id',
                'fecha_atencion': 'fecha_solicitud',
                'fecha_cierre': 'fecha_resolucion',
                'categoria': 'categoria',
                'estatus': 'estado',
                'duracion': 'tiempo_atencion_horas'
            },
            'db3': {
                'id_seguimiento': 'solicitud_id',
                'fecha_registro': 'fecha_solicitud',
                'fecha_finalizacion': 'fecha_resolucion',
                'tipo': 'categoria',
                'estado_actual': 'estado',
                'tiempo_total': 'tiempo_atencion_horas'
            }
        }
        
        mapping = column_mappings.get(source, {})
        df_standardized = df.rename(columns=mapping)
        
        # Asegurar columnas esenciales
        essential_columns = [
            'solicitud_id', 'fecha_solicitud', 'fecha_resolucion',
            'categoria', 'estado', 'tiempo_atencion_horas'
        ]
        
        for col in essential_columns:
            if col not in df_standardized.columns:
                df_standardized[col] = None
        
        return df_standardized[essential_columns]
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y normaliza los datos consolidados.
        
        Args:
            df: DataFrame a limpiar
            
        Returns:
            DataFrame limpio
        """
        # Convertir fechas
        date_columns = ['fecha_solicitud', 'fecha_resolucion']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calcular tiempo de atención si no existe
        if df['tiempo_atencion_horas'].isna().all():
            df['tiempo_atencion_horas'] = (
                df['fecha_resolucion'] - df['fecha_solicitud']
            ).dt.total_seconds() / 3600
        
        # Eliminar duplicados
        df = df.drop_duplicates(subset=['solicitud_id'], keep='first')
        
        # Eliminar registros sin fecha de solicitud
        df = df.dropna(subset=['fecha_solicitud'])
        
        logger.info(f"Datos limpios: {len(df)} registros válidos")
        return df
    
    def load(self, df: pd.DataFrame) -> str:
        """
        Carga los datos procesados en archivos.
        
        Args:
            df: DataFrame consolidado a guardar
            
        Returns:
            Ruta del archivo guardado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar como CSV
        csv_path = self.processed_data_dir / f"consolidated_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Datos consolidados guardados en {csv_path}")
        
        # Guardar también como Excel para facilitar revisión
        excel_path = self.processed_data_dir / f"consolidated_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False)
        logger.info(f"Datos consolidados guardados en {excel_path}")
        
        # Guardar último archivo procesado (referencia)
        latest_path = self.processed_data_dir / "consolidated_latest.csv"
        df.to_csv(latest_path, index=False)
        
        return str(csv_path)
    
    def run(self) -> str:
        """
        Ejecuta el pipeline ETL completo.
        
        Returns:
            Ruta del archivo de datos consolidados
        """
        logger.info("Iniciando pipeline ETL...")
        
        # Extract
        raw_data = self.extract()
        
        # Transform
        consolidated_data = self.transform(raw_data)
        
        # Load
        output_path = self.load(consolidated_data)
        
        logger.info(f"Pipeline ETL completado. Datos en: {output_path}")
        return output_path


def main():
    """Función principal para ejecutar el pipeline."""
    try:
        pipeline = ETLPipeline()
        output_path = pipeline.run()
        print(f"Pipeline completado exitosamente. Datos en: {output_path}")
    except Exception as e:
        logger.error(f"Error en pipeline ETL: {str(e)}")
        raise


if __name__ == "__main__":
    main()
