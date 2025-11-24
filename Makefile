ENV_VARS=UV_CACHE_DIR=$(CURDIR)/.uvcache TMP=$(CURDIR)/.tmp TEMP=$(CURDIR)/.tmp

.PHONY: env-dirs install dev-install migrate collectstatic run render-start build lint lint-fix test coverage ci-install ci-migrate ci-test

env-dirs:
	@python - <<'PY'
from pathlib import Path
for name in (".uvcache", ".tmp"):
    Path(name).mkdir(parents=True, exist_ok=True)
PY

install: env-dirs
	$(ENV_VARS) uv sync

dev-install: env-dirs
	$(ENV_VARS) uv sync --group dev

migrate:
	$(ENV_VARS) uv run python manage.py migrate

collectstatic:
	$(ENV_VARS) uv run python manage.py collectstatic --noinput

run:
	uv run python manage.py runserver

render-start:
# 	uv run gunicorn task_manager.wsgi
	uv run waitress-serve --listen=0.0.0.0 task_manager.wsgi:application

build:
	./build.sh

lint: env-dirs
	$(ENV_VARS) uv run ruff check

lint-fix: env-dirs
	$(ENV_VARS) uv run ruff check --fix

test: env-dirs
	$(ENV_VARS) uv run pytest --ds=task_manager.settings --reuse-db

coverage: env-dirs
	$(ENV_VARS) uv run coverage run --omit='*/migrations/*,*/settings.py,*/venv/*,*/.venv/*' -m pytest --ds=task_manager.settings
	$(ENV_VARS) uv run coverage report --show-missing --skip-covered

ci-install: env-dirs
	$(ENV_VARS) uv sync --group dev

ci-migrate: env-dirs
	$(ENV_VARS) uv run python manage.py makemigrations --noinput && \
	$(ENV_VARS) uv run python manage.py migrate --noinput

ci-test: env-dirs
	$(ENV_VARS) uv run coverage run --omit='*/migrations/*,*/settings.py,*/venv/*,*/.venv/*' -m pytest --ds=task_manager.settings --reuse-db
	$(ENV_VARS) uv run coverage xml
	$(ENV_VARS) uv run coverage report --show-missing --skip-covered
