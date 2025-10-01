.PHONY: help install test lint format clean run-etl run-kpi run-train run-predict

help:
	@echo "Comandos disponibles:"
	@echo "  make install       - Instalar dependencias"
	@echo "  make test          - Ejecutar pruebas"
	@echo "  make lint          - Verificar código con flake8"
	@echo "  make format        - Formatear código con black"
	@echo "  make clean         - Limpiar archivos temporales"
	@echo "  make run-etl       - Ejecutar pipeline ETL"
	@echo "  make run-kpi       - Calcular KPIs"
	@echo "  make run-train     - Entrenar modelo predictivo"
	@echo "  make run-predict   - Generar predicciones"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503

format:
	black src/ tests/ --line-length=100
	isort src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage

run-etl:
	python -m src.data_ingestion.etl_pipeline

run-kpi:
	python -m src.analysis.kpi_calculator

run-train:
	python -m src.models.train_model

run-predict:
	python -m src.models.predict
