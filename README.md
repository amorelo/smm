# Sistema de Monitoreo Municipal (SMM)

## Descripción

Sistema para consolidar información histórica de tiempos de atención ciudadana, identificar tendencias y anticipar la demanda mediante análisis predictivo.

## Características

- **Ingesta de Datos**: Conectores para tres bases de datos existentes
- **Análisis de Tiempos**: Mapeo y consolidación de tiempos de atención
- **KPIs**: Definición y cálculo de indicadores clave de desempeño
- **Modelo Predictivo**: Anticipación de demanda ciudadana
- **Supervisión**: Panel de monitoreo de la Secretaría

## Estructura del Proyecto

```
smm/
├── config/              # Archivos de configuración
├── data/
│   ├── raw/            # Datos crudos (no versionados)
│   └── processed/      # Datos procesados (no versionados)
├── models/
│   └── saved/          # Modelos entrenados (no versionados)
├── reports/
│   └── generated/      # Reportes generados (no versionados)
├── src/
│   ├── data_ingestion/ # Conectores y ETL
│   ├── analysis/       # Análisis y KPIs
│   └── models/         # Modelos predictivos
└── tests/              # Pruebas unitarias
```

## Requisitos

- Python 3.8+
- Ver `requirements.txt` para dependencias completas

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/amorelo/smm.git
cd smm

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

1. Copiar el archivo de configuración de ejemplo:
```bash
cp config/config.example.yaml config/config.yaml
```

2. Editar `config/config.yaml` con las credenciales de las bases de datos

## Uso

### Ingesta de Datos

```bash
python -m src.data_ingestion.etl_pipeline
```

### Análisis y KPIs

```bash
python -m src.analysis.kpi_calculator
```

### Entrenamiento del Modelo Predictivo

```bash
python -m src.models.train_model
```

### Generación de Predicciones

```bash
python -m src.models.predict
```

## KPIs Implementados

1. **Tiempo Promedio de Atención**: Tiempo medio de resolución de solicitudes
2. **Tasa de Resolución**: Porcentaje de solicitudes resueltas
3. **Tiempo de Espera**: Tiempo promedio desde solicitud hasta atención
4. **Demanda por Categoría**: Distribución de solicitudes por tipo
5. **Tendencias Temporales**: Patrones de demanda por día/hora/mes

## Modelo Predictivo

El modelo predictivo utiliza técnicas de machine learning para anticipar:
- Volumen de solicitudes futuras
- Tiempos de atención esperados
- Recursos necesarios por período

### Características del Modelo

- Algoritmo: Ensemble (Random Forest + Gradient Boosting)
- Ventana temporal: 30 días históricos
- Horizonte de predicción: 7-30 días
- Métricas de evaluación: RMSE, MAE, R²

## Desarrollo

### Ejecutar Pruebas

```bash
pytest tests/
```

### Agregar Nuevos Conectores

1. Crear nuevo archivo en `src/data_ingestion/connectors/`
2. Implementar clase que herede de `BaseConnector`
3. Registrar en `src/data_ingestion/connector_factory.py`

## Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto es de uso interno para la gestión municipal.

## Contacto

Para consultas y soporte, contactar al equipo de desarrollo.