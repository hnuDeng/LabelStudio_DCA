.PHONY: setup test lint clean build-frontend

setup:
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r ../requirements.txt
	cd frontend && npm install

test:
	cd backend && pytest ../tests/

lint:
	cd backend && flake8 .
	cd frontend && npm run lint

build-frontend:
	cd frontend && npm run build

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/dist
