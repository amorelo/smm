"""
Setup para el Sistema de Monitoreo Municipal.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="smm",
    version="1.0.0",
    author="Equipo de Desarrollo SMM",
    description="Sistema de Monitoreo Municipal para consolidación de tiempos de atención y predicción de demanda",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amorelo/smm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Government",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "smm-etl=src.data_ingestion.etl_pipeline:main",
            "smm-kpi=src.analysis.kpi_calculator:main",
            "smm-train=src.models.train_model:main",
            "smm-predict=src.models.predict:main",
        ],
    },
)
