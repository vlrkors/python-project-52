#!/usr/bin/env bash
set -euo pipefail

# Install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

# Install dependencies & prepare project.
# В окружении сборки Render нет доступа к базе, поэтому миграции выполняются
# перед запуском сервиса (см. цель render-start). Здесь ограничиваемся
# установкой зависимостей и сборкой статики.
make install && make collectstatic
