"""
Setup script for DiabetesTwin project
Install and configure the complete Digital Twin application
"""

from setuptools import setup, find_packages

setup(
    name="digitaltwin",
    version="1.0.0",
    description="AI-Powered Digital Twin for Type 2 Diabetes Management",
    author="DiabetesTwin Team",
    author_email="team@digitaltwin.health",
    url="https://github.com/yourusername/digitaltwin",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "pydantic==2.5.3",
        "python-dotenv==1.0.0",
        "pandas==2.1.4",
        "numpy==1.26.3",
        "scikit-learn==1.3.2",
        "xgboost==2.0.3",
        "tensorflow==2.15.0",
        "keras==2.15.0",
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "python-multipart==0.0.6",
        "websockets==12.0",
        "faker==22.2.0",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "black==23.12.0",
            "flake8==6.1.0",
            "mypy==1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "digitaltwin=backend.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
