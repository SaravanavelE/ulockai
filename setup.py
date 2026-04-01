from setuptools import setup, find_packages
from pathlib import Path

long_description = Path("README.md").read_text(encoding="utf-8")

setup(
    name="ulockai",
    version="0.1.1",
    packages=find_packages(),
    description="Production-ready AI Security SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
)