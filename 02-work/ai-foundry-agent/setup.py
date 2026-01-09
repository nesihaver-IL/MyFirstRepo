"""Setup configuration for AI Foundry Agent."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-foundry-agent",
    version="1.0.0",
    author="Your Organization",
    description="Knowledge Hub Agent using Azure AI Foundry with RAG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "azure-ai-projects>=1.0.0b1",
        "azure-identity>=1.19.0",
        "azure-search-documents>=11.6.0",
        "openai>=1.58.1",
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "pydantic>=2.10.1",
        "pydantic-settings>=2.6.1",
        "python-dotenv>=1.0.1",
        "tenacity>=9.0.0",
    ],
)
