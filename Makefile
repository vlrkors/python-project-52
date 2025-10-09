.PHONY: install start render-start migrate collectstatic makemigrations build lint format test

install:
	uv sync

start:
	python manage.py runserver 0.0.0.0:8000

render-start:
	gunicorn task_manager.wsgi

migrate:
	python manage.py migrate --noinput

makemigrations:
	python manage.py makemigrations

collectstatic:
	python manage.py collectstatic --noinput

build:
	./build.sh

lint:
	@echo "Add your linter here (flake8/ruff)"

format:
	@echo "Add your formatter here (black/isort)"

test:
	@echo "No tests yet"
