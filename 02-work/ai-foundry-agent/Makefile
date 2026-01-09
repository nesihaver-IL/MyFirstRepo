.PHONY: help install dev-install test lint format run clean deploy

help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code"
	@echo "  run          - Run the API server"
	@echo "  clean        - Clean build artifacts"
	@echo "  deploy       - Deploy to Azure"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

run:
	python -m src.api.main

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .coverage htmlcov/

deploy:
	@echo "Deploying to Azure..."
	az deployment group create \
		--resource-group $(AZURE_RESOURCE_GROUP) \
		--template-file infrastructure/main.bicep \
		--parameters @infrastructure/parameters.json
