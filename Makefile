SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -Command

ENV_VARS = $$env:UV_CACHE_DIR="$(CURDIR)/.uvcache"; $$env:TMP="$(CURDIR)/.tmp"; $$env:TEMP="$(CURDIR)/.tmp";
PYTHON = $(CURDIR)/.venv/Scripts/python.exe

.PHONY: env-dirs install dev-install migrate collectstatic run render-start build lint lint-fix test coverage ci-install ci-migrate ci-test

env-dirs:
	@python -c "from pathlib import Path; [Path(n).mkdir(parents=True, exist_ok=True) for n in ('.uvcache', '.tmp')]"

install: env-dirs
	$(ENV_VARS) & "$(PYTHON)" -m uv sync

dev-install: env-dirs
	$(ENV_VARS) & "$(PYTHON)" -m uv sync --group dev

migrate: env-dirs
	$(ENV_VARS) & "$(PYTHON)" manage.py migrate

collectstatic: env-dirs
	$(ENV_VARS) & "$(PYTHON)" manage.py collectstatic --noinput

run:
	& "$(PYTHON)" manage.py runserver

render-start:
	# & "$(PYTHON)" -m gunicorn task_manager.wsgi
	& "$(PYTHON)" -m waitress --listen=0.0.0.0 task_manager.wsgi:application

build:
	./build.sh

lint: env-dirs
	$(ENV_VARS) & "$(PYTHON)" -m ruff check

lint-fix: env-dirs
	$(ENV_VARS) & "$(PYTHON)" -m ruff check --fix

test: env-dirs
	$(ENV_VARS) & "$(PYTHON)" -m pytest --ds=task_manager.settings --reuse-db

coverage: env-dirs
	$(ENV_VARS) & "$(PYTHON)" -m coverage run --omit='*/migrations/*,*/settings.py,*/venv/*,*/.venv/*' -m pytest --ds=task_manager.settings
	$(ENV_VARS) & "$(PYTHON)" -m coverage report --show-missing --skip-covered

ci-install: env-dirs
	$(ENV_VARS) & "$(PYTHON)" -m uv sync --group dev

ci-migrate: env-dirs
	$(ENV_VARS) & "$(PYTHON)" manage.py makemigrations --noinput; $(ENV_VARS) & "$(PYTHON)" manage.py migrate --noinput

ci-test: env-dirs
	$(ENV_VARS) & "$(PYTHON)" -m coverage run --omit='*/migrations/*,*/settings.py,*/venv/*,*/.venv/*' -m pytest --ds=task_manager.settings --reuse-db
	$(ENV_VARS) & "$(PYTHON)" -m coverage xml
	$(ENV_VARS) & "$(PYTHON)" -m coverage report --show-missing --skip-covered
