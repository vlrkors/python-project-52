#!/usr/bin/env bash

curl -LsSf https://astral.sh/uv/install.sh | sh

# uv installer drops a helper script as $HOME/.local/bin/env on Unix-like hosts.
# On some setups (e.g. Git Bash on Windows) it may not exist, so guard it and
# still add uv to PATH.
if [[ -f "$HOME/.local/bin/env" ]]; then
  # shellcheck source=/dev/null
  source "$HOME/.local/bin/env"
else
  export PATH="$HOME/.local/bin:$PATH"
fi

make install && make collectstatic && make migrate
