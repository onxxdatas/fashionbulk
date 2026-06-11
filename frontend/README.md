# FashionBulk Frontend

Static HTML/CSS frontend for FashionBulk wholesale clothing platform.

## Files
- `index.html` — single-page app
- `index.css` — all styles

## Before deploying

In `index.html`, update the API URL on line 4 of the `<script>`:

```js
const API = "https://api.onxxdatas.space"; // already set correctly
```

For local development, change it to:
```js
const API = "http://localhost:8000";
```

---

## Deploy to Netlify

### Option A — Netlify UI (drag & drop)
1. Go to https://app.netlify.com
2. Drag the `frontend/` folder onto the Netlify dashboard
3. Your site is live instantly at a `*.netlify.app` URL

### Option B — Netlify CLI
```bash
npm install -g netlify-cli
cd frontend/
netlify deploy --prod --dir .
```

---

## Current Netlify URL
Your frontend is currently live at:
https://salomyangi.netlify.app/

## Link your custom domain in Netlify
1. Open Netlify → Site settings → Domain management
2. Click Add custom domain
3. Enter your real domain name, for example `yourdomain.com`

## DNS record to add in your registrar
In your Namecheap (or other registrar) DNS panel, add:
```
Type:  CNAME
Name:  www
Value: salomyangi.netlify.app
```

If Netlify shows root-domain records, add those exact A/ALIAS records too.

Or if you want it at the root:
```
Type:  A
Name:  @
Value: 75.2.60.5   (Netlify's load balancer IP)
```

### 3. Enable HTTPS
Netlify provisions a free Let's Encrypt cert automatically once DNS propagates (usually 5–30 min).

---

## Final URLs

| Service | URL |
|---------|-----|
| Frontend | https://fashionbulk.onxxdatas.space |
| Backend API | https://api.onxxdatas.space |
| API Docs | https://api.onxxdatas.space/docs |
