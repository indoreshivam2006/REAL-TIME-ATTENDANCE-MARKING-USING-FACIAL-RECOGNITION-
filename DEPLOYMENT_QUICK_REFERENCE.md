# 🚀 Quick Deployment Reference Card

## Railway Backend Deployment

### 1️⃣ Setup (5 min)
- Go to https://railway.app
- Login with GitHub
- New Project → Deploy from GitHub repo
- Select your repository

### 2️⃣ Configure (3 min)
- Settings → Root Directory: `backend`
- Variables → Add all environment variables
- Settings → Networking → Generate Domain

### 3️⃣ Deploy (10 min)
- Auto-deploys after configuration
- Wait for green checkmark
- Copy your Railway URL

## Netlify Frontend Deployment

### 1️⃣ Setup (3 min)
- Go to https://netlify.com
- Login with GitHub
- Add new site → Import from GitHub
- Select your repository

### 2️⃣ Configure (2 min)
- Base directory: `frontend`
- Add environment variable:
  - `NEXT_PUBLIC_API_URL` = Your Railway URL

### 3️⃣ Deploy (5 min)
- Click "Deploy site"
- Wait for build to complete
- Copy your Netlify URL

## Connect Frontend & Backend

### Update Backend CORS
Railway → Variables → Edit `CORS_ORIGINS`:
```
https://your-netlify-app.netlify.app,http://localhost:3000
```

### Verify Frontend API URL
Netlify → Environment variables → Check:
```
NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
```

### Redeploy Both
- Railway: Auto-redeploys on variable change
- Netlify: Trigger deploy → Deploy site

## Test Connection
1. Open Netlify URL
2. Press F12 (console)
3. Try login
4. Check for CORS errors
5. Test all features

## Environment Variables Checklist

### Railway (Backend)
- [ ] FLASK_SECRET_KEY
- [ ] FLASK_DEBUG=False
- [ ] CORS_ORIGINS (with Netlify URL)
- [ ] FACE_RECOGNITION_MODE=cnn
- [ ] CNN_SIMILARITY_THRESHOLD=0.35
- [ ] FACE_RECOGNITION_THRESHOLD=110
- [ ] MIN_FACE_SIZE=20
- [ ] SCALE_FACTOR=1.05
- [ ] MIN_NEIGHBORS=3

### Netlify (Frontend)
- [ ] NEXT_PUBLIC_API_URL (Railway URL)

## Common Issues

### CORS Error
→ Update Railway `CORS_ORIGINS` with Netlify URL

### API calls to localhost
→ Update Netlify `NEXT_PUBLIC_API_URL` with Railway URL

### Build fails
→ Check logs, verify environment variables

### Slow deployment
→ Normal for first deploy (PyTorch is large)

## Your URLs

```
Frontend: https://_________________.netlify.app
Backend:  https://_________________.up.railway.app
GitHub:   https://github.com/indoreshivam2006/REAL-TIME-ATTENDANCE-MARKING-USING-FACIAL-RECOGNITION-
```

---

**Total Time: ~30-40 minutes**

For detailed instructions, see: `RAILWAY_NETLIFY_DEPLOYMENT.md`
