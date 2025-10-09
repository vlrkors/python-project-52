#!/usr/bin/env bash
set -euo pipefail

# Install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

# Install dependencies & prepare project
make install && make collectstatic && make migrate
