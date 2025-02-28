# setup.py
from setuptools import setup, find_packages

setup(
    name="investment-service",
    version="0.1.0",
    description="Investment Service for Wealth Manager Platform",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.23",
        "pydantic>=2.0.0",
        "psycopg2-binary>=2.9.1",
        "python-jose[cryptography]>=3.3.0",
        "python-multipart>=0.0.5",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
        ],
    },
)