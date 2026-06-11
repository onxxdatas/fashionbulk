# FashionBulk

This repo now includes a basic CI/CD pipeline for GitHub → EC2 deployment.

Current frontend URL on Netlify:
https://salomyangi.netlify.app/

## What is configured
- GitHub Actions validates backend syntax on every push to `main`
- The same workflow deploys the `backend/`, `frontend/`, and `scripts/` folders to your EC2 instance
- The EC2 deploy script installs Python dependencies, restarts the FastAPI service, and reloads Nginx

## GitHub secrets to add
Create these repository secrets in GitHub:
- `EC2_HOST`: your EC2 public IP or DNS name
- `EC2_USER`: the SSH user (usually `ubuntu`)
- `EC2_SSH_KEY`: the private SSH key for the EC2 instance

## Deploy
Push to `main` and GitHub Actions will run automatically.

You can also run the workflow manually from the Actions tab.

## Domain setup on your registrar
Use these DNS records:
- `api` → `A` record → your EC2 public IP
- `www` → `CNAME` record → `salomyangi.netlify.app`

This lets you expose:
- `https://api.yourdomain.com` for the FastAPI backend
- `https://yourdomain.com` for the Netlify frontend
