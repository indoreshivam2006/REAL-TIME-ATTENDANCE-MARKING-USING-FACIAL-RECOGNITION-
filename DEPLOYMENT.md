# 🚀 Quick Deployment Guide

For detailed deployment instructions, see the [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)

## Quick Start

### Frontend (Netlify)
1. Push code to GitHub
2. Connect repository to Netlify
3. Set base directory: `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL`
5. Deploy!

### Backend (Render.com - Recommended)
1. Create account on Render.com
2. Connect GitHub repository
3. Set root directory: `backend`
4. Add environment variables
5. Deploy!

## Important Files Created

- ✅ `netlify.toml` - Netlify configuration
- ✅ `backend/Procfile` - Backend deployment config
- ✅ `backend/runtime.txt` - Python version
- ✅ `frontend/.env.example` - Frontend env template
- ✅ `backend/.env.example` - Backend env template

## Need Help?

See the complete [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for:
- Step-by-step instructions with screenshots
- Multiple backend deployment options
- Troubleshooting guide
- Environment variable setup
- Post-deployment configuration

---

**Note**: Netlify cannot host Flask backends. Use Render.com, Railway.app, or PythonAnywhere for the backend.
