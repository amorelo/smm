# Documentación Técnica - Sistema de Monitoreo Municipal (SMM)

## Índice

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Módulos](#módulos)
3. [Flujo de Datos](#flujo-de-datos)
4. [Base de Datos](#base-de-datos)
5. [KPIs](#kpis)
6. [Modelo Predictivo](#modelo-predictivo)
7. [API y Endpoints](#api-y-endpoints)

## Arquitectura del Sistema

El Sistema de Monitoreo Municipal (SMM) está diseñado con una arquitectura modular que permite:

- **Escalabilidad**: Agregar nuevas fuentes de datos o KPIs fácilmente
- **Mantenibilidad**: Módulos independientes con responsabilidades claras
- **Extensibilidad**: Arquitectura basada en interfaces y factory patterns

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                  Sistema de Monitoreo Municipal         │
└─────────────────────────────────────────────────────────┘
           │
           ├── Ingesta de Datos (ETL)
           │   ├── Conectores (PostgreSQL, MySQL, SQL Server)
           │   ├── Extracción
           │   ├── Transformación
           │   └── Carga
           │
           ├── Análisis y KPIs
           │   ├── Calculador de KPIs
           │   ├── Análisis de Tendencias
           │   └── Generación de Reportes
           │
           └── Modelos Predictivos
               ├── Preparación de Características
               ├── Entrenamiento (Ensemble)
               ├── Evaluación
               └── Predicción
```

## Módulos

### 1. Módulo de Ingesta de Datos (`src/data_ingestion`)

**Responsabilidad**: Extraer, transformar y consolidar datos de múltiples fuentes.

#### Componentes:

- **BaseConnector**: Clase abstracta base para conectores
- **Conectores Específicos**: PostgreSQL, MySQL, SQL Server
- **ConnectorFactory**: Factory para crear instancias de conectores
- **ETLPipeline**: Orquestador del proceso ETL

#### Flujo ETL:

1. **Extracción**: Conecta a cada base de datos y extrae registros históricos
2. **Transformación**: 
   - Estandariza nombres de columnas
   - Limpia y normaliza datos
   - Consolida múltiples fuentes
3. **Carga**: Guarda datos procesados en formato CSV y Excel

### 2. Módulo de Análisis (`src/analysis`)

**Responsabilidad**: Calcular KPIs y analizar tendencias.

#### KPICalculator:

Calcula 5 KPIs principales:

1. **Tiempo Promedio de Atención**
   - Media, mediana, desviación estándar
   - Porcentaje dentro del umbral
   
2. **Tasa de Resolución**
   - Porcentaje de solicitudes resueltas
   - Comparación con meta
   
3. **Tiempo de Espera**
   - Tiempo promedio para solicitudes pendientes
   
4. **Demanda por Categoría**
   - Distribución absoluta y porcentual
   - Categoría de mayor demanda
   
5. **Tendencias Temporales**
   - Patrones por día de semana
   - Patrones por hora del día
   - Patrones mensuales y anuales

### 3. Módulo de Modelos Predictivos (`src/models`)

**Responsabilidad**: Entrenar y generar predicciones de demanda.

#### DemandPredictor:

**Algoritmo**: Ensemble de Random Forest y Gradient Boosting

**Características utilizadas**:
- Temporales: año, mes, día, día de semana, hora, trimestre
- Ventanas móviles: solicitudes últimos 7, 14, 30 días
- Categóricas: categoría, estado, fuente (codificadas)

**Proceso**:
1. Preparación de características
2. División train/test (80/20)
3. Entrenamiento de ambos modelos
4. Ensemble (promedio de predicciones)
5. Evaluación (RMSE, MAE, R²)

## Flujo de Datos

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   DB1        │     │   DB2        │     │   DB3        │
│ (PostgreSQL) │     │  (MySQL)     │     │ (SQL Server) │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  ETL Pipeline  │
                    │  - Extract     │
                    │  - Transform   │
                    │  - Load        │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ Datos          │
                    │ Consolidados   │
                    └───────┬────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌───────▼────────┐ ┌────▼──────┐ ┌─────▼────────┐
    │ KPI Calculator │ │  Training │ │ Predictions  │
    └───────┬────────┘ └────┬──────┘ └─────┬────────┘
            │               │               │
    ┌───────▼────────┐ ┌────▼──────┐ ┌─────▼────────┐
    │   Reportes     │ │  Modelo   │ │  Predicciones│
    │   de KPIs      │ │ Entrenado │ │   Futuras    │
    └────────────────┘ └───────────┘ └──────────────┘
```

## Base de Datos

### Esquema Consolidado

Después del proceso ETL, los datos se consolidan en el siguiente esquema:

```
consolidated_data
├── solicitud_id (string): ID único de la solicitud
├── fecha_solicitud (datetime): Fecha de creación de la solicitud
├── fecha_resolucion (datetime): Fecha de resolución (puede ser null)
├── categoria (string): Categoría de la solicitud
├── estado (string): Estado actual (Resuelto, Pendiente)
├── tiempo_atencion_horas (float): Tiempo de atención en horas
└── fuente (string): Base de datos de origen (db1, db2, db3)
```

### Mapeo de Columnas por Fuente

**DB1 (PostgreSQL - Solicitudes)**:
- `id_solicitud` → `solicitud_id`
- `fecha_creacion` → `fecha_solicitud`
- `fecha_resolucion` → `fecha_resolucion`
- `tipo_solicitud` → `categoria`
- `estado` → `estado`
- `tiempo_atencion` → `tiempo_atencion_horas`

**DB2 (MySQL - Atención Ciudadana)**:
- `id_atencion` → `solicitud_id`
- `fecha_atencion` → `fecha_solicitud`
- `fecha_cierre` → `fecha_resolucion`
- `categoria` → `categoria`
- `estatus` → `estado`
- `duracion` → `tiempo_atencion_horas`

**DB3 (SQL Server - Seguimiento)**:
- `id_seguimiento` → `solicitud_id`
- `fecha_registro` → `fecha_solicitud`
- `fecha_finalizacion` → `fecha_resolucion`
- `tipo` → `categoria`
- `estado_actual` → `estado`
- `tiempo_total` → `tiempo_atencion_horas`

## KPIs

### Definición de Métricas

#### 1. Tiempo Promedio de Atención

**Fórmula**: 
```
TPÁ = Σ(tiempo_atencion) / n_solicitudes_resueltas
```

**Interpretación**:
- < 24 horas: Excelente
- 24-48 horas: Bueno (dentro de umbral)
- > 48 horas: Requiere atención

#### 2. Tasa de Resolución

**Fórmula**:
```
TR = (solicitudes_resueltas / total_solicitudes) × 100
```

**Meta**: 85%

**Interpretación**:
- ≥ 85%: Cumple meta
- < 85%: No cumple meta

#### 3. Tiempo de Espera

**Fórmula**:
```
TE = Σ(fecha_actual - fecha_solicitud) / n_solicitudes_pendientes
```

**Uso**: Identificar solicitudes que requieren atención urgente

#### 4. Demanda por Categoría

**Análisis**:
- Distribución absoluta
- Distribución porcentual
- Categoría de mayor demanda
- Evolución temporal

#### 5. Tendencias Temporales

**Dimensiones**:
- Día de la semana (lunes-domingo)
- Hora del día (0-23)
- Mes del año
- Año

**Uso**: 
- Identificar patrones estacionales
- Optimizar asignación de recursos
- Planificar capacidad

## Modelo Predictivo

### Arquitectura del Modelo

**Tipo**: Ensemble Learning

**Componentes**:
1. Random Forest Regressor
2. Gradient Boosting Regressor
3. Promedio de predicciones (ensemble)

### Hiperparámetros

```yaml
n_estimators: 100
max_depth: 10
learning_rate: 0.1 (GB)
random_state: 42
```

### Características (Features)

**Temporales** (8):
- año, mes, día
- día_semana, hora
- trimestre, día_del_año, semana_del_año

**Ventanas Móviles** (3):
- solicitudes_ultimos_7d
- solicitudes_ultimos_14d
- solicitudes_ultimos_30d

**Categóricas** (3):
- categoria_encoded
- estado_encoded
- fuente_encoded

**Total**: 14 características

### Métricas de Evaluación

1. **RMSE** (Root Mean Squared Error):
   - Penaliza errores grandes
   - Mismas unidades que la variable objetivo (horas)

2. **MAE** (Mean Absolute Error):
   - Error promedio absoluto
   - Más robusto a outliers

3. **R²** (Coeficiente de Determinación):
   - Proporción de varianza explicada
   - Rango: 0-1 (1 = perfecto)

### Proceso de Entrenamiento

1. **Carga de datos**: Datos consolidados históricos
2. **Preparación**: 
   - Extracción de características
   - Codificación de variables categóricas
   - Normalización (si necesario)
3. **División**: 80% entrenamiento, 20% prueba
4. **Entrenamiento**: 
   - Random Forest
   - Gradient Boosting
5. **Evaluación**: Métricas en conjunto de prueba
6. **Guardado**: Modelos y encoders en disco

### Generación de Predicciones

**Input**: Número de días a predecir (default: 30)

**Output**: DataFrame con:
- fecha: Fecha de la predicción
- categoria: Categoría de solicitud
- tiempo_atencion_predicho: Predicción ensemble
- prediccion_rf: Predicción Random Forest
- prediccion_gb: Predicción Gradient Boosting

**Formato**: CSV, Excel, YAML (resumen)

## API y Endpoints

### Comandos de Consola

El sistema se instala con comandos de consola:

```bash
# Ejecutar ETL
smm-etl

# Calcular KPIs
smm-kpi

# Entrenar modelo
smm-train

# Generar predicciones
smm-predict
```

### Comandos Make

```bash
# Instalar dependencias
make install

# Ejecutar pruebas
make test

# Verificar código
make lint

# Formatear código
make format

# Limpiar archivos temporales
make clean

# Ejecutar pipeline ETL
make run-etl

# Calcular KPIs
make run-kpi

# Entrenar modelo
make run-train

# Generar predicciones
make run-predict
```

## Configuración

### Archivo de Configuración (config.yaml)

```yaml
databases:
  db1:
    type: postgresql
    host: ${DB1_HOST}
    port: 5432
    database: solicitudes_db
    username: ${DB1_USER}
    password: ${DB1_PASSWORD}

etl:
  raw_data_dir: data/raw
  processed_data_dir: data/processed
  extraction_frequency: 24  # horas

kpis:
  tiempo_atencion_umbral: 48  # horas
  tasa_resolucion_meta: 85  # porcentaje

model:
  algorithm: ensemble
  training_window: 180  # días
  prediction_horizon: 30  # días
```

### Variables de Entorno

Crear archivo `.env`:

```bash
# Base de datos 1
DB1_USER=usuario1
DB1_PASSWORD=password1

# Base de datos 2
DB2_USER=usuario2
DB2_PASSWORD=password2

# Base de datos 3
DB3_USER=usuario3
DB3_PASSWORD=password3
```

## Mantenimiento y Operación

### Frecuencia de Ejecución Recomendada

- **ETL**: Diario (automatizar con cron)
- **KPIs**: Semanal
- **Entrenamiento**: Mensual
- **Predicciones**: Semanal o según demanda

### Monitoreo

Revisar logs en:
- `logs/smm.log`

### Troubleshooting

**Problema**: Error de conexión a base de datos
**Solución**: Verificar credenciales en `.env` y conectividad de red

**Problema**: Error al entrenar modelo
**Solución**: Verificar que existan datos suficientes (mínimo 100 registros)

**Problema**: Predicciones imprecisas
**Solución**: Reentrenar modelo con más datos históricos

## Extensibilidad

### Agregar Nuevo Conector

1. Crear clase heredando de `BaseConnector`
2. Implementar métodos abstractos
3. Registrar en `ConnectorFactory`

### Agregar Nuevo KPI

1. Agregar método en `KPICalculator`
2. Actualizar `calculate_all_kpis()`
3. Documentar en README

### Agregar Nuevas Características al Modelo

1. Modificar `prepare_features()` en `DemandPredictor`
2. Reentrenar modelo
3. Evaluar impacto en métricas

## Licencia y Contacto

Sistema de uso interno para gestión municipal.

Para soporte técnico, contactar al equipo de desarrollo.
