# 🚀 RideSwift Deployment Checklist

Follow this checklist to deploy your application quickly!

## 📋 Pre-Deployment Checklist

- [ ] Code is committed to Git
- [ ] All tests are passing
- [ ] Environment variables are documented
- [ ] README is up to date

## 🎯 Quick Start (Recommended Path)

### 1. Database Setup (5 minutes)
- [ ] Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [ ] Create free cluster
- [ ] Add database user
- [ ] Whitelist IPs (0.0.0.0/0 for now)
- [ ] Copy connection string

### 2. Deploy Backend to Railway (10 minutes)
```bash
# Run from backend directory
cd backend

# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

- [ ] Set environment variables in Railway dashboard:
  - `MONGODB_URL`: Your MongoDB connection string
  - `DATABASE_NAME`: `rideswift_db`
  - `SECRET_KEY`: Generate a secure key
  - `BACKEND_CORS_ORIGINS`: `["http://localhost:3000"]` (update after frontend deploy)

- [ ] Note your backend URL: `https://your-app.railway.app`

### 3. Deploy Frontend to Vercel (5 minutes)
```bash
# Run from project root
cd ..

# Create production env file
echo "NEXT_PUBLIC_API_URL=https://your-backend.railway.app" > .env.production

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

- [ ] Note your frontend URL: `https://your-app.vercel.app`

### 4. Update Backend CORS (2 minutes)
```bash
# Update CORS in Railway
railway variables set BACKEND_CORS_ORIGINS='["https://your-app.vercel.app"]'
```

## ✅ Post-Deployment Verification

- [ ] Backend health check: `curl https://your-backend.railway.app/health`
- [ ] Frontend loads: Visit `https://your-app.vercel.app`
- [ ] Can create account
- [ ] Can sign in
- [ ] Can book a ride

## 🔧 Optional Enhancements

### Add Redis (for caching)
- [ ] Create account at [Redis Cloud](https://redis.com/try-free/)
- [ ] Add `REDIS_URL` to Railway environment

### Add Custom Domain
- [ ] Frontend: Vercel Dashboard → Settings → Domains
- [ ] Backend: Railway Dashboard → Settings → Domains

### Enable Monitoring
- [ ] Add Sentry for error tracking
- [ ] Add Google Analytics for usage tracking

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS Error | Update `BACKEND_CORS_ORIGINS` with your frontend URL |
| Database Connection Failed | Check MongoDB whitelist and connection string |
| Build Failed | Check logs in Railway/Vercel dashboard |
| Login Not Working | Ensure frontend has correct `NEXT_PUBLIC_API_URL` |

## 📞 Need Help?

1. Check `DEPLOYMENT.md` for detailed instructions
2. Review logs in your hosting dashboard
3. Verify all environment variables are set correctly

---

**Estimated Total Time: 20-30 minutes** ⏱️

Ready? Run `./deploy-quick-start.sh` for automated deployment! 🚀
