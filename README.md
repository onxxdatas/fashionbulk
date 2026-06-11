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
- `NETLIFY_AUTH_TOKEN`: your Netlify personal access token
- `NETLIFY_SITE_ID`: your Netlify site ID

### How to get the Netlify secrets
1. In Netlify, open User settings → Applications → Personal access tokens
2. Create a token and copy it as `NETLIFY_AUTH_TOKEN`
3. Open your site → Site settings → General → Site details
4. Copy the Site ID and save it as `NETLIFY_SITE_ID`

## Deploy
Push to `main` and GitHub Actions will run automatically.

You can also run the workflow manually from the Actions tab.

## Domain setup on your registrar
Use these DNS records for the live custom domain setup:
- `@` → `A` record → `75.2.60.5` and `99.83.190.102` (Netlify root-domain IPs)
- `www` → `CNAME` record → `salomyangi.netlify.app`
- `api` → `A` record → your EC2 public IP

This lets you expose:
- `https://api.onxxdatas.space` for the FastAPI backend
- `https://onxxdatas.space` (or `https://www.onxxdatas.space`) for the Netlify frontend

After changing DNS, wait 5–30 minutes for propagation, then add the custom domain in Netlify → Site settings → Domain management.
