.PHONY: run test fmt lint
run: 
	uvicorn app.main:app --reload

test: 
	pytest

fmt: 
	python -m pip install ruff black || true; ruff check app tests --fix || true; black app tests || true

lint:
	flake8 app/
