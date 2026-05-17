#!/usr/bin/env bash
set -euo pipefail

systemctl stop wangdaooj-backend.service 2>/dev/null || true
systemctl stop wangdaooj-frontend.service 2>/dev/null || true

cat >/etc/systemd/system/wangdaooj-backend.service <<'EOF'
[Unit]
Description=WangDaoOJ Django backend
After=network.target postgresql.service

[Service]
User=yhk
WorkingDirectory=/mnt/d/Projects/OnlineJudge/backend
Environment=PATH=/home/yhk/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=UV_PROJECT_ENVIRONMENT=.venv-linux
ExecStart=/home/yhk/.local/bin/uv run python manage.py runserver 0.0.0.0:8000 --noreload
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

cat >/etc/systemd/system/wangdaooj-frontend.service <<'EOF'
[Unit]
Description=WangDaoOJ frontend static server
After=network.target

[Service]
User=yhk
WorkingDirectory=/mnt/d/Projects/OnlineJudge/frontend
ExecStart=/usr/bin/python3 -m http.server 5173 --bind 0.0.0.0 --directory /mnt/d/Projects/OnlineJudge/frontend/dist
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now wangdaooj-backend.service
systemctl enable --now wangdaooj-frontend.service
systemctl --no-pager --full status wangdaooj-backend.service wangdaooj-frontend.service
