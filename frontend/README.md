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

## Link your domain (onxxdatas.space)

### 1. Add custom domain in Netlify
- Netlify Dashboard → Site settings → Domain management → Add custom domain
- Enter: `fashionbulk.onxxdatas.space`

### 2. Add DNS record at your registrar
In your DNS panel for `onxxdatas.space`, add:
```
Type:  CNAME
Name:  fashionbulk
Value: <your-netlify-site>.netlify.app
```

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
