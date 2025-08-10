# RideSwift Deployment Guide

This guide will help you deploy the RideSwift application to production.

## Prerequisites

Before deploying, ensure you have:
- A MongoDB database (MongoDB Atlas recommended)
- A Redis instance (Redis Cloud recommended)
- API keys for Twilio and SendGrid (if using notifications)

## 1. Database Setup (MongoDB Atlas)

### Create a MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new cluster (free tier available)
4. Whitelist all IPs (0.0.0.0/0) for development or specific IPs for production
5. Create a database user with read/write permissions
6. Get your connection string (it will look like: `mongodb+srv://username:password@cluster.mongodb.net/database`)

## 2. Redis Setup (Redis Cloud)

### Create a Redis Cloud Account
1. Go to [Redis Cloud](https://redis.com/try-free/)
2. Sign up for a free account
3. Create a new database (free tier available)
4. Get your Redis URL (it will look like: `redis://default:password@redis-server.com:port`)

## 3. Backend Deployment

### Option A: Deploy to Railway (Recommended)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Create a new project**:
   ```bash
   cd backend
   railway init
   ```

4. **Create a `railway.json` file**:
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
     }
   }
   ```

5. **Set environment variables**:
   ```bash
   railway variables set MONGODB_URL="your-mongodb-url"
   railway variables set REDIS_URL="your-redis-url"
   railway variables set SECRET_KEY="your-secret-key"
   railway variables set BACKEND_CORS_ORIGINS="https://your-frontend-url.vercel.app"
   ```

6. **Deploy**:
   ```bash
   railway up
   ```

7. **Get your backend URL**:
   ```bash
   railway open
   ```

### Option B: Deploy to Render

1. **Create a `render.yaml` file** in the backend directory:
   ```yaml
   services:
     - type: web
       name: rideswift-api
       env: python
       buildCommand: "pip install -r requirements.txt"
       startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: MONGODB_URL
           sync: false
         - key: REDIS_URL
           sync: false
         - key: SECRET_KEY
           generateValue: true
         - key: BACKEND_CORS_ORIGINS
           sync: false
   ```

2. **Push to GitHub** and connect to Render
3. **Set environment variables** in Render dashboard
4. **Deploy** from Render dashboard

### Option C: Deploy to Heroku

1. **Create a `Procfile`** in the backend directory:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Create a `runtime.txt`**:
   ```
   python-3.11.9
   ```

3. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku config:set MONGODB_URL="your-mongodb-url"
   heroku config:set REDIS_URL="your-redis-url"
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set BACKEND_CORS_ORIGINS="https://your-frontend-url.vercel.app"
   git push heroku main
   ```

## 4. Frontend Deployment

### Option A: Deploy to Vercel (Recommended)

1. **Create a `.env.production` file** in the root directory:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```

2. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Select your account
   - Link to existing project or create new
   - Confirm settings
   - Deploy!

5. **Set environment variables** in Vercel dashboard:
   - Go to your project settings
   - Add `NEXT_PUBLIC_API_URL` with your backend URL

### Option B: Deploy to Netlify

1. **Create a `netlify.toml` file**:
   ```toml
   [build]
     command = "npm run build"
     publish = ".next"

   [[plugins]]
     package = "@netlify/plugin-nextjs"

   [build.environment]
     NEXT_PUBLIC_API_URL = "https://your-backend-url.railway.app"
   ```

2. **Install Netlify CLI**:
   ```bash
   npm i -g netlify-cli
   ```

3. **Deploy**:
   ```bash
   netlify deploy --prod
   ```

### Option C: Deploy to AWS Amplify

1. **Push your code to GitHub**

2. **Go to AWS Amplify Console**

3. **Connect your GitHub repository**

4. **Configure build settings**:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm install
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: .next
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```

5. **Set environment variables**:
   - Add `NEXT_PUBLIC_API_URL` with your backend URL

## 5. Post-Deployment Configuration

### Update CORS Origins

After deploying your frontend, update your backend's CORS settings:

1. **Get your frontend URL** (e.g., `https://your-app.vercel.app`)

2. **Update backend environment variable**:
   ```bash
   BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]
   ```

### Setup Celery Workers (Optional)

If you need background tasks:

1. **For Railway**, add a new service for Celery:
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "celery -A app.core.celery_app worker --loglevel=info"
     }
   }
   ```

2. **For Heroku**, add a worker dyno:
   ```
   worker: celery -A app.core.celery_app worker --loglevel=info
   ```

### Monitor Your Application

1. **Setup monitoring** with services like:
   - Sentry (error tracking)
   - LogRocket (session replay)
   - DataDog (performance monitoring)

2. **Check logs**:
   - Railway: `railway logs`
   - Heroku: `heroku logs --tail`
   - Vercel: Check dashboard

## 6. Environment Variables Reference

### Backend (.env)
```
# Database
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/rideswift
DATABASE_NAME=rideswift_db

# Redis
REDIS_URL=redis://default:password@redis-server.com:port

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Services (optional)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+918143243584
SENDGRID_API_KEY=your-sendgrid-key
STRIPE_SECRET_KEY=your-stripe-key
```

### Frontend (.env.production)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## 7. Testing Your Deployment

1. **Test the backend**:
   ```bash
   curl https://your-backend.railway.app/health
   ```

2. **Test the frontend**:
   - Visit your frontend URL
   - Try signing up/signing in
   - Test booking functionality

## 8. Troubleshooting

### Common Issues

1. **CORS errors**: Make sure your frontend URL is in `BACKEND_CORS_ORIGINS`
2. **Database connection**: Check MongoDB whitelist and connection string
3. **Redis connection**: Verify Redis URL and credentials
4. **Environment variables**: Ensure all required variables are set
5. **Build failures**: Check logs for specific errors

### Debug Commands

```bash
# Check backend logs
railway logs  # or heroku logs --tail

# Test API endpoints
curl https://your-backend.railway.app/api/v1/docs

# Check environment variables
railway variables  # or heroku config
```

## 9. Custom Domain Setup

### Frontend (Vercel)
1. Go to project settings
2. Add your domain
3. Update DNS records as instructed

### Backend (Railway)
1. Go to project settings
2. Add custom domain
3. Update DNS CNAME record

## 10. SSL/HTTPS

Both Vercel and Railway provide automatic SSL certificates. For custom domains, SSL is also automatically provisioned.

## Conclusion

Your RideSwift application should now be deployed and accessible! Remember to:
- Keep your environment variables secure
- Monitor your application logs
- Set up proper error tracking
- Configure backup strategies for your database
- Consider implementing CI/CD for automated deployments

For support, check the documentation of your chosen hosting providers or reach out to their support teams.
