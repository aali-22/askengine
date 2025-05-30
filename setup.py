from setuptools import setup, find_packages

setup(
    name="askengine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "requests>=2.31.0",
        "SQLAlchemy>=2.0.0",
        "typer>=0.9.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "spacy>=3.7.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
    ],
    python_requires=">=3.8",
) 