# FashionBulk Backend

FastAPI backend for the FashionBulk wholesale clothing platform.

## Local development

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

## Deploy on AWS EC2

### 1. Launch EC2 instance
- AMI: Ubuntu 22.04 LTS
- Instance type: t2.micro (free tier) or t3.small
- Security Group — open inbound ports:
  - 22 (SSH)
  - 80 (HTTP)
  - 443 (HTTPS)
  - 8000 (optional, for direct API access during testing)

### 2. SSH into your instance
```bash
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>
```

### 3. Install dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx certbot python3-certbot-nginx -y
```

### 4. Upload code
```bash
# From your local machine:
scp -i your-key.pem -r ./backend ubuntu@<EC2-PUBLIC-IP>:/home/ubuntu/fashionbulk
```

### 5. Set up Python environment
```bash
cd /home/ubuntu/fashionbulk
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Run with systemd (auto-restart on reboot)
```bash
sudo nano /etc/systemd/system/fashionbulk.service
```

Paste this:
```
[Unit]
Description=FashionBulk FastAPI
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/fashionbulk
ExecStart=/home/ubuntu/fashionbulk/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable fashionbulk
sudo systemctl start fashionbulk
```

### 7. Configure Nginx as reverse proxy
```bash
sudo nano /etc/nginx/sites-available/fashionbulk
```

Paste this:
```nginx
server {
    listen 80;
    server_name api.onxxdatas.space;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/fashionbulk /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. Add HTTPS with Let's Encrypt
```bash
sudo certbot --nginx -d api.onxxdatas.space
```

### 9. DNS — point your domain to EC2
In your domain registrar (onxxdatas.space), add an A record:
```
api.onxxdatas.space  →  <EC2-PUBLIC-IP>
```

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | — | Register new buyer |
| POST | /auth/login | — | Login, returns token |
| POST | /auth/logout | Bearer | Logout |
| GET | /products | — | List all products |
| GET | /products/{id} | — | Get single product |
| POST | /products | Admin | Create product |
| DELETE | /products/{id} | Admin | Delete product |
| GET | /categories | — | List categories |
| POST | /orders | Bearer | Place an order |
| GET | /orders | Bearer | List my orders |
| GET | /orders/{id} | Bearer | Get order detail |
| PATCH | /orders/{id}/status | Admin | Update order status |
| GET | /admin/stats | Admin | Dashboard stats |
| GET | /health | — | Health check |

Default admin credentials:
- Email: admin@fashionbulk.com
- Password: admin123
