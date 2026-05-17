#!/usr/bin/env bash
set -euo pipefail

cd /mnt/d/Projects/OnlineJudge/backend
export PATH="$HOME/.local/bin:$PATH"
export UV_PROJECT_ENVIRONMENT=.venv-linux

uv run python manage.py runserver 0.0.0.0:8000
