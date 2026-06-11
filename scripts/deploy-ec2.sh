#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${HOME}/fashionbulk"
FRONTEND_DIR="/var/www/fashionbulk"
SERVICE_FILE="/etc/systemd/system/fashionbulk.service"
NGINX_SITE="/etc/nginx/sites-available/fashionbulk"
SERVICE_USER="$(whoami)"

echo "[1/6] Ensuring directories exist"
sudo mkdir -p "$APP_DIR" "$FRONTEND_DIR" /etc/nginx/sites-available /etc/nginx/sites-enabled

cd "$APP_DIR"

echo "[2/6] Installing system packages needed for Python venv"
for attempt in 1 2 3 4 5; do
  if sudo fuser /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/cache/apt/archives/lock >/dev/null 2>&1; then
    echo "apt lock is busy; waiting 10 seconds (attempt $attempt/5)..."
    sleep 10
    continue
  fi

  sudo DEBIAN_FRONTEND=noninteractive apt-get update && \
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3-venv python3-pip nginx build-essential && break

  echo "apt install failed; retrying in 10 seconds (attempt $attempt/5)..."
  sleep 10
 done

PYTHON_BIN="$(command -v python3 || true)"
if [ -z "$PYTHON_BIN" ] || ! "$PYTHON_BIN" -m venv --help >/dev/null 2>&1; then
  echo "No usable Python venv interpreter is available on this EC2 instance" >&2
  exit 1
fi

echo "[3/6] Installing backend dependencies"
"$PYTHON_BIN" -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install --only-binary=:all: -r backend/requirements.txt

echo "[4/6] Syncing frontend to Nginx root"
sudo rm -rf "$FRONTEND_DIR"/*
sudo mkdir -p "$FRONTEND_DIR"
sudo cp -r "$APP_DIR/frontend/." "$FRONTEND_DIR/"

echo "[6/6] Creating systemd service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=FashionBulk FastAPI
After=network.target

[Service]
User=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable fashionbulk || true
sudo systemctl restart fashionbulk

echo "[7/7] Configuring Nginx"
sudo tee "$NGINX_SITE" > /dev/null <<'EOF'
server {
    listen 80;
    server_name fashionbulk.onxxdatas.space;
    root /var/www/fashionbulk;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 80;
    server_name api.onxxdatas.space;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sfn "$NGINX_SITE" /etc/nginx/sites-enabled/fashionbulk
sudo nginx -t
sudo systemctl reload nginx

echo "Deployment finished."
