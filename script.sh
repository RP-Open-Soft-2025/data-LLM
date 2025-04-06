#!/bin/bash



  nginx_conf="
  server {
    listen 80;
    client_max_body_size 10M;

    location / {
      proxy_pass http://localhost:8080;
      proxy_connect_timeout 300s;
      proxy_read_timeout 300s;
      proxy_send_timeout 300s;
    }
  }
  "

if ! command -v nginx >/dev/null; then
  sudo apt-get update
  sudo apt-get install -y nginx
fi

sudo -u root bash -c "echo '$nginx_conf' >/etc/nginx/sites-available/default"

if systemctl is-active -q ngin  x; then
  sudo systemctl restart nginx
else
  sudo systemctl enable --now nginx
fi
