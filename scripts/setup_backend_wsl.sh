#!/usr/bin/env bash
set -euo pipefail

cd /mnt/d/Projects/OnlineJudge/backend
export PATH="$HOME/.local/bin:$PATH"
export UV_PROJECT_ENVIRONMENT=.venv-linux

uv sync
uv run python manage.py migrate
uv run python manage.py seed_demo
