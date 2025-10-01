# smm# Análisis avanzado de datos y forecasting para mejorar niveles de servicio y definir KPIs operacionales

## Resumen

Esta propuesta tiene como propósito desarrollar un sistema integral de medición, análisis y pronóstico de los tiempos de atención ciudadana en las sedes de la Secretaría de Movilidad, en el contexto de la primera reversión de operador en 20 años. A partir de cuatro bases de datos operacionales, se aplicarán metodologías de series temporales, clustering y simulación para identificar patrones semanales, mensuales y semestrales. El resultado será un dashboard interactivo con KPIs clave y un modelo de forecasting capaz de anticipar la ocupación de cada sede, orientando la asignación de recursos y la definición de métricas contractuales.

**Palabras clave:**
- Tiempos de atención
- Series temporales
- Forecasting
- KPIs de servicio
- Dashboard interactivo
- Simulación de colas
- Análisis de patrones

## Introducción

La reversión del operador de la Secretaría de Movilidad tras dos décadas inaugura la necesidad de contar con métricas robustas que garanticen niveles de servicio óptimos y condiciones contractuales favorables. Actualmente no se dispone de un sistema que consolide la información histórica de tiempos de atención para identificar tendencias y anticipar la demanda ciudadana. Este proyecto busca llenar ese vacío mediante el aprovechamiento de tres bases de datos existentes, la supervisión de la Secretaría, con el fin de mapear tiempos, definir KPIs y entregar un modelo predictivo antes del cambio de gestión.

## Objetivos

**General:** Desarrollar un sistema de análisis y pronóstico de los tiempos de atención ciudadana en las sedes de la Secretaría de Movilidad, que permita mejorar niveles de servicio y soportar la definición de métricas contractuales al nuevo operador.

**Específicos:**
1. Integrar, limpiar y consolidar las tres fuentes de datos disponibles para construir una base unificada de tiempos de atención.
2. Realizar un análisis descriptivo de patrones temporales (semanales, mensuales y semestrales) de ocupación y tiempos de espera.
3. Implementar modelos de series temporales y técnicas de machine learning para pronosticar la ocupación y los tiempos promedio de atención.
4. Diseñar un dashboard interactivo con KPIs clave que facilite la supervisión y la toma de decisiones por parte de la Secretaría y el operador.
5. Validar y ajustar el modelo junto con la supervisión de la Secretaría de Movilidad y el equipo del operador antes de la entrega final.

## Marco Teórico

En este apartado se revisarán los fundamentos de:
- Series temporales y modelos ARIMA/Prophet para forecasting de demanda y tiempos de servicio.
- Técnicas de clustering y segmentación de patrones de atención.
- Simulación de colas aplicada a la gestión de filas y tiempos de espera.
- Definición y seguimiento de KPIs de nivel de servicio (tiempo promedio de atención, tasa de abandono, ocupación de recursos).
- Principios de Lean Six Sigma para la optimización de procesos.

Se emplearán normas APA para las citas y referencias de estudios clave que sustentan cada técnica.

## Metodología

El proyecto seguirá un enfoque cuantitativo con herramientas de análisis de datos y BI, dividido en cinco fases:
1. Preparación de datos
2. Análisis exploratorio y definición de KPIs
3. Modelado y forecasting
4. Desarrollo de dashboard interactivo
5. Validación y ajustes

### Cronograma de actividades
- **Mes 1:** Integración y limpieza de las cuatro bases de datos. Análisis exploratorio y definición de métricas clave.
- **Mes 2:** Implementación de modelos de series temporales y clustering. Construcción y automatización del dashboard en Power BI.
- **Mes 3:** Pruebas, validación con supervisión y refinamiento de modelos.
- **Mes 4:** Documentación final y entrega antes del proceso de reversión.

### Presupuesto
- **Recursos humanos:** 1 ingeniero industrial (120 h), 1 profesional especializado (80 h).
- **Infraestructura:** servidor virtual en la nube y almacenamiento.
- **Licencias de software:** Power BI Pro, bibliotecas Python/R.
- **Materiales:** equipo de oficina y costos de reuniones de seguimiento.

## Resultados Esperados
- Mapa de tiempos promedio de atención con patrón semanal, mensual y semestral.
- Modelos predictivos con error de pronóstico inferior al 10 % para ocupación y tiempos.
- Dashboard interactivo con KPIs en tiempo real para supervisión y gestión.
- Recomendaciones de optimización de recursos y planificación según demanda anticipada.
- Base analítica para definir y negociar indicadores de desempeño contractual con el nuevo operador.
