# Guía de Inicio Rápido - SMM

## Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/amorelo/smm.git
cd smm
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

O usando Make:

```bash
make install
```

### 4. Configurar bases de datos

Crear archivo `.env` en la raíz del proyecto:

```bash
# Base de datos 1 (PostgreSQL)
DB1_USER=tu_usuario
DB1_PASSWORD=tu_contraseña

# Base de datos 2 (MySQL)
DB2_USER=tu_usuario
DB2_PASSWORD=tu_contraseña

# Base de datos 3 (SQL Server)
DB3_USER=tu_usuario
DB3_PASSWORD=tu_contraseña
```

Copiar y editar el archivo de configuración:

```bash
cp config/config.example.yaml config/config.yaml
```

Editar `config/config.yaml` con las direcciones y puertos de tus bases de datos.

## Uso Básico

### Flujo Completo

#### 1. Ejecutar ETL (Extracción, Transformación y Carga)

```bash
python -m src.data_ingestion.etl_pipeline
```

O con Make:

```bash
make run-etl
```

Esto:
- Conectará a las tres bases de datos
- Extraerá los datos históricos
- Los transformará y consolidará
- Guardará los resultados en `data/processed/`

#### 2. Calcular KPIs

```bash
python -m src.analysis.kpi_calculator
```

O con Make:

```bash
make run-kpi
```

Genera un reporte con:
- Tiempo promedio de atención
- Tasa de resolución
- Tiempo de espera
- Demanda por categoría
- Tendencias temporales

Reporte guardado en: `reports/generated/kpi_report_[timestamp].yaml`

#### 3. Entrenar Modelo Predictivo

```bash
python -m src.models.train_model
```

O con Make:

```bash
make run-train
```

Entrena el modelo usando:
- Random Forest
- Gradient Boosting
- Ensemble de ambos

Guarda:
- Modelos entrenados en `models/saved/`
- Métricas de evaluación en `reports/generated/`

#### 4. Generar Predicciones

```bash
python -m src.models.predict
```

O con Make:

```bash
make run-predict
```

Genera predicciones para los próximos 30 días por defecto.

Resultados en:
- `reports/generated/predictions_[timestamp].csv`
- `reports/generated/predictions_[timestamp].xlsx`
- `reports/generated/predictions_summary_[timestamp].yaml`

## Uso Avanzado

### Ejecutar con Parámetros Personalizados

#### ETL con configuración personalizada

```python
from src.data_ingestion import ETLPipeline

pipeline = ETLPipeline(config_path="config/mi_config.yaml")
output_path = pipeline.run()
print(f"Datos guardados en: {output_path}")
```

#### KPIs con datos específicos

```python
from src.analysis import KPICalculator

calculator = KPICalculator()
calculator.load_data("data/processed/mi_archivo.csv")
kpis = calculator.calculate_all_kpis()
print(kpis)
```

#### Predicciones personalizadas

```python
from src.models.train_model import DemandPredictor

predictor = DemandPredictor()
predictor.load_data()
predictor.train(test_size=0.3)  # 30% para prueba
predictions = predictor.predict_demand(days_ahead=60)  # 60 días
print(predictions.head())
```

## Pruebas

Ejecutar todas las pruebas:

```bash
pytest tests/ -v
```

Con cobertura:

```bash
pytest tests/ -v --cov=src --cov-report=html
```

O con Make:

```bash
make test
```

## Desarrollo

### Formatear código

```bash
make format
```

### Verificar estilo

```bash
make lint
```

### Limpiar archivos temporales

```bash
make clean
```

## Automatización

### Programar Ejecución con Cron (Linux/Mac)

Editar crontab:

```bash
crontab -e
```

Agregar líneas:

```bash
# ETL diario a las 2 AM
0 2 * * * cd /ruta/al/smm && /ruta/al/venv/bin/python -m src.data_ingestion.etl_pipeline

# KPIs semanales (lunes a las 6 AM)
0 6 * * 1 cd /ruta/al/smm && /ruta/al/venv/bin/python -m src.analysis.kpi_calculator

# Predicciones semanales (lunes a las 7 AM)
0 7 * * 1 cd /ruta/al/smm && /ruta/al/venv/bin/python -m src.models.predict
```

### Programar con Windows Task Scheduler

1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Configurar trigger (diario, semanal, etc.)
4. Acción: Iniciar programa
   - Programa: `C:\ruta\al\venv\Scripts\python.exe`
   - Argumentos: `-m src.data_ingestion.etl_pipeline`
   - Iniciar en: `C:\ruta\al\smm`

## Monitoreo

### Ver logs

Los logs se guardan en `logs/smm.log` (configurar en `config.yaml`).

```bash
tail -f logs/smm.log
```

### Verificar estado de datos

```bash
# Ver último archivo procesado
ls -lh data/processed/consolidated_latest.csv

# Ver estadísticas básicas
python -c "import pandas as pd; df = pd.read_csv('data/processed/consolidated_latest.csv'); print(df.describe())"
```

### Verificar modelos

```bash
# Listar modelos guardados
ls -lh models/saved/

# Verificar último modelo
python -c "import joblib; model = joblib.load('models/saved/random_forest_latest.joblib'); print(f'Modelo con {model.n_estimators} estimadores')"
```

## Troubleshooting

### Error: No module named 'src'

Asegurarse de ejecutar desde la raíz del proyecto:

```bash
cd /ruta/al/smm
python -m src.data_ingestion.etl_pipeline
```

### Error: Connection refused (base de datos)

1. Verificar que la base de datos está corriendo
2. Verificar credenciales en `.env`
3. Verificar host y puerto en `config/config.yaml`
4. Verificar conectividad de red

```bash
# Probar conexión PostgreSQL
psql -h localhost -U usuario -d base_datos

# Probar conexión MySQL
mysql -h localhost -u usuario -p base_datos
```

### Error: Not enough data

El modelo requiere al menos 100 registros históricos con tiempo de atención conocido.

Verificar:

```bash
python -c "import pandas as pd; df = pd.read_csv('data/processed/consolidated_latest.csv'); print(f'Registros totales: {len(df)}'); print(f'Con tiempo de atención: {df['tiempo_atencion_horas'].notna().sum()}')"
```

### Predicciones poco precisas

1. Reentrenar con más datos históricos
2. Ajustar hiperparámetros en `config/config.yaml`
3. Verificar calidad de datos de entrada
4. Considerar agregar más características

## Próximos Pasos

1. Revisar la [Documentación Técnica](TECHNICAL_DOCS.md)
2. Explorar los reportes generados
3. Personalizar KPIs según necesidades
4. Ajustar modelo predictivo
5. Crear dashboards con los datos

## Soporte

Para preguntas o problemas:
1. Revisar logs en `logs/smm.log`
2. Consultar documentación técnica
3. Contactar al equipo de desarrollo
