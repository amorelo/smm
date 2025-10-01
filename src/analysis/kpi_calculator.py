"""
Calculador de KPIs para el Sistema de Monitoreo Municipal.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from pathlib import Path
import yaml
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KPICalculator:
    """Calculador de indicadores clave de desempeño."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Inicializa el calculador de KPIs.
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.kpi_config = self.config['kpis']
        self.data = None
    
    def load_data(self, data_path: str = None) -> pd.DataFrame:
        """
        Carga los datos consolidados.
        
        Args:
            data_path: Ruta al archivo de datos. Si es None, carga el último procesado.
            
        Returns:
            DataFrame con los datos cargados
        """
        if data_path is None:
            data_path = Path(self.config['etl']['processed_data_dir']) / 'consolidated_latest.csv'
        
        self.data = pd.read_csv(data_path)
        
        # Convertir fechas
        self.data['fecha_solicitud'] = pd.to_datetime(self.data['fecha_solicitud'])
        self.data['fecha_resolucion'] = pd.to_datetime(self.data['fecha_resolucion'])
        
        logger.info(f"Datos cargados: {len(self.data)} registros")
        return self.data
    
    def calculate_tiempo_promedio_atencion(self) -> Dict:
        """
        Calcula el tiempo promedio de atención.
        
        Returns:
            Diccionario con el KPI y métricas relacionadas
        """
        if self.data is None:
            raise ValueError("Datos no cargados. Llamar load_data() primero.")
        
        # Filtrar solo solicitudes resueltas
        resolved = self.data[self.data['fecha_resolucion'].notna()].copy()
        
        resultado = {
            'nombre': 'Tiempo Promedio de Atención',
            'valor_promedio': resolved['tiempo_atencion_horas'].mean(),
            'mediana': resolved['tiempo_atencion_horas'].median(),
            'desviacion_std': resolved['tiempo_atencion_horas'].std(),
            'minimo': resolved['tiempo_atencion_horas'].min(),
            'maximo': resolved['tiempo_atencion_horas'].max(),
            'umbral': self.kpi_config['tiempo_atencion_umbral'],
            'dentro_umbral_pct': (
                (resolved['tiempo_atencion_horas'] <= self.kpi_config['tiempo_atencion_umbral']).sum() 
                / len(resolved) * 100
            ),
            'unidad': 'horas',
            'fecha_calculo': datetime.now().isoformat()
        }
        
        logger.info(f"Tiempo promedio de atención: {resultado['valor_promedio']:.2f} horas")
        return resultado
    
    def calculate_tasa_resolucion(self) -> Dict:
        """
        Calcula la tasa de resolución de solicitudes.
        
        Returns:
            Diccionario con el KPI y métricas relacionadas
        """
        if self.data is None:
            raise ValueError("Datos no cargados. Llamar load_data() primero.")
        
        total_solicitudes = len(self.data)
        solicitudes_resueltas = self.data['fecha_resolucion'].notna().sum()
        tasa = (solicitudes_resueltas / total_solicitudes * 100) if total_solicitudes > 0 else 0
        
        resultado = {
            'nombre': 'Tasa de Resolución',
            'valor': tasa,
            'total_solicitudes': total_solicitudes,
            'solicitudes_resueltas': int(solicitudes_resueltas),
            'solicitudes_pendientes': int(total_solicitudes - solicitudes_resueltas),
            'meta': self.kpi_config['tasa_resolucion_meta'],
            'cumple_meta': tasa >= self.kpi_config['tasa_resolucion_meta'],
            'unidad': 'porcentaje',
            'fecha_calculo': datetime.now().isoformat()
        }
        
        logger.info(f"Tasa de resolución: {resultado['valor']:.2f}%")
        return resultado
    
    def calculate_tiempo_espera(self) -> Dict:
        """
        Calcula el tiempo de espera promedio.
        
        Returns:
            Diccionario con el KPI y métricas relacionadas
        """
        if self.data is None:
            raise ValueError("Datos no cargados. Llamar load_data() primero.")
        
        # Para solicitudes pendientes, calcular tiempo desde solicitud hasta ahora
        pendientes = self.data[self.data['fecha_resolucion'].isna()].copy()
        
        if len(pendientes) > 0:
            pendientes['tiempo_espera'] = (
                datetime.now() - pendientes['fecha_solicitud']
            ).dt.total_seconds() / 3600
            
            tiempo_espera_promedio = pendientes['tiempo_espera'].mean()
        else:
            tiempo_espera_promedio = 0
        
        resultado = {
            'nombre': 'Tiempo de Espera Promedio',
            'valor_promedio': tiempo_espera_promedio,
            'solicitudes_en_espera': len(pendientes),
            'tiempo_espera_max': pendientes['tiempo_espera'].max() if len(pendientes) > 0 else 0,
            'unidad': 'horas',
            'fecha_calculo': datetime.now().isoformat()
        }
        
        logger.info(f"Tiempo de espera promedio: {resultado['valor_promedio']:.2f} horas")
        return resultado
    
    def calculate_demanda_por_categoria(self) -> Dict:
        """
        Calcula la distribución de demanda por categoría.
        
        Returns:
            Diccionario con el KPI y distribución por categoría
        """
        if self.data is None:
            raise ValueError("Datos no cargados. Llamar load_data() primero.")
        
        distribucion = self.data['categoria'].value_counts().to_dict()
        distribucion_pct = (self.data['categoria'].value_counts(normalize=True) * 100).to_dict()
        
        resultado = {
            'nombre': 'Demanda por Categoría',
            'distribucion_absoluta': distribucion,
            'distribucion_porcentual': distribucion_pct,
            'categoria_mayor_demanda': max(distribucion, key=distribucion.get) if distribucion else None,
            'total_categorias': len(distribucion),
            'fecha_calculo': datetime.now().isoformat()
        }
        
        logger.info(f"Distribución calculada para {resultado['total_categorias']} categorías")
        return resultado
    
    def calculate_tendencias_temporales(self) -> Dict:
        """
        Calcula tendencias temporales de demanda.
        
        Returns:
            Diccionario con tendencias por día, hora y mes
        """
        if self.data is None:
            raise ValueError("Datos no cargados. Llamar load_data() primero.")
        
        df = self.data.copy()
        
        # Extraer componentes temporales
        df['dia_semana'] = df['fecha_solicitud'].dt.day_name()
        df['hora'] = df['fecha_solicitud'].dt.hour
        df['mes'] = df['fecha_solicitud'].dt.month_name()
        df['anio'] = df['fecha_solicitud'].dt.year
        
        resultado = {
            'nombre': 'Tendencias Temporales',
            'demanda_por_dia_semana': df['dia_semana'].value_counts().to_dict(),
            'demanda_por_hora': df.groupby('hora').size().to_dict(),
            'demanda_por_mes': df['mes'].value_counts().to_dict(),
            'tendencia_anual': df.groupby('anio').size().to_dict(),
            'fecha_calculo': datetime.now().isoformat()
        }
        
        logger.info("Tendencias temporales calculadas")
        return resultado
    
    def calculate_all_kpis(self) -> Dict:
        """
        Calcula todos los KPIs definidos.
        
        Returns:
            Diccionario con todos los KPIs
        """
        logger.info("Calculando todos los KPIs...")
        
        kpis = {
            'tiempo_promedio_atencion': self.calculate_tiempo_promedio_atencion(),
            'tasa_resolucion': self.calculate_tasa_resolucion(),
            'tiempo_espera': self.calculate_tiempo_espera(),
            'demanda_por_categoria': self.calculate_demanda_por_categoria(),
            'tendencias_temporales': self.calculate_tendencias_temporales(),
        }
        
        logger.info("Todos los KPIs calculados exitosamente")
        return kpis
    
    def generate_report(self, output_path: str = None) -> str:
        """
        Genera un reporte con todos los KPIs.
        
        Args:
            output_path: Ruta donde guardar el reporte
            
        Returns:
            Ruta del reporte generado
        """
        kpis = self.calculate_all_kpis()
        
        if output_path is None:
            reports_dir = Path(self.config['reports']['output_dir'])
            reports_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = reports_dir / f"kpi_report_{timestamp}.yaml"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(kpis, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Reporte de KPIs generado en: {output_path}")
        return str(output_path)


def main():
    """Función principal para calcular KPIs."""
    try:
        calculator = KPICalculator()
        calculator.load_data()
        report_path = calculator.generate_report()
        print(f"Reporte de KPIs generado en: {report_path}")
    except Exception as e:
        logger.error(f"Error al calcular KPIs: {str(e)}")
        raise


if __name__ == "__main__":
    main()
