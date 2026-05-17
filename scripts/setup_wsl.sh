#!/usr/bin/env bash
set -euo pipefail

pg_ctlcluster 16 main start || true

if ! su - postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='online_judge'\"" | grep -q 1; then
  su - postgres -c "psql -c \"CREATE USER online_judge WITH PASSWORD 'online_judge';\""
fi

if ! su - postgres -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='online_judge'\"" | grep -q 1; then
  su - postgres -c "createdb -O online_judge online_judge"
fi

pg_isready
g++ --version | head -n 1
