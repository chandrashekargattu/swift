#!/bin/bash

echo "🚀 RideSwift Quick Deployment Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${BLUE}This script will help you deploy your RideSwift application${NC}"
echo ""

# Step 1: Choose deployment option
echo -e "${YELLOW}Step 1: Choose your deployment option${NC}"
echo "1) Full deployment (Frontend + Backend + Database)"
echo "2) Frontend only (Vercel)"
echo "3) Backend only (Railway)"
read -p "Enter your choice (1-3): " deployment_choice

case $deployment_choice in
    1)
        echo -e "\n${GREEN}Full deployment selected${NC}"
        
        # MongoDB Atlas setup reminder
        echo -e "\n${YELLOW}Step 2: MongoDB Atlas Setup${NC}"
        echo "1. Go to https://www.mongodb.com/cloud/atlas"
        echo "2. Create a free cluster"
        echo "3. Get your connection string"
        read -p "Enter your MongoDB connection string: " MONGODB_URL
        
        # Redis setup reminder
        echo -e "\n${YELLOW}Step 3: Redis Setup (Optional)${NC}"
        echo "1. Go to https://redis.com/try-free/"
        echo "2. Create a free database"
        echo "3. Get your Redis URL (or press Enter to skip)"
        read -p "Enter your Redis URL (optional): " REDIS_URL
        
        # Deploy Backend
        echo -e "\n${YELLOW}Step 4: Deploying Backend to Railway${NC}"
        
        if ! command_exists railway; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        
        cd backend
        
        # Create railway.json
        cat > railway.json << EOF
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
  }
}
EOF
        
        echo "Logging into Railway..."
        railway login
        
        echo "Initializing Railway project..."
        railway init
        
        echo "Setting environment variables..."
        railway variables set MONGODB_URL="$MONGODB_URL"
        railway variables set DATABASE_NAME="rideswift_db"
        railway variables set SECRET_KEY="$(openssl rand -hex 32)"
        railway variables set ENVIRONMENT="production"
        
        if [ ! -z "$REDIS_URL" ]; then
            railway variables set REDIS_URL="$REDIS_URL"
        fi
        
        echo "Deploying backend..."
        railway up
        
        echo -e "${GREEN}Backend deployed!${NC}"
        echo "Getting backend URL..."
        BACKEND_URL=$(railway open --json | jq -r '.url')
        echo "Backend URL: $BACKEND_URL"
        
        cd ..
        
        # Deploy Frontend
        echo -e "\n${YELLOW}Step 5: Deploying Frontend to Vercel${NC}"
        
        if ! command_exists vercel; then
            echo "Installing Vercel CLI..."
            npm install -g vercel
        fi
        
        # Create .env.production
        echo "NEXT_PUBLIC_API_URL=https://$BACKEND_URL" > .env.production
        
        echo "Deploying to Vercel..."
        vercel --prod
        
        echo -e "\n${GREEN}✅ Deployment Complete!${NC}"
        echo -e "${BLUE}Your application is now live!${NC}"
        
        # Update CORS
        echo -e "\n${YELLOW}Final Step: Update CORS${NC}"
        echo "1. Get your Vercel URL from above"
        echo "2. Run: railway variables set BACKEND_CORS_ORIGINS='[\"https://your-app.vercel.app\"]'"
        ;;
        
    2)
        echo -e "\n${GREEN}Frontend deployment selected${NC}"
        
        read -p "Enter your backend URL: " BACKEND_URL
        
        if ! command_exists vercel; then
            echo "Installing Vercel CLI..."
            npm install -g vercel
        fi
        
        echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.production
        
        echo "Deploying to Vercel..."
        vercel --prod
        
        echo -e "\n${GREEN}✅ Frontend deployed!${NC}"
        ;;
        
    3)
        echo -e "\n${GREEN}Backend deployment selected${NC}"
        
        read -p "Enter your MongoDB connection string: " MONGODB_URL
        read -p "Enter your frontend URL (for CORS): " FRONTEND_URL
        
        if ! command_exists railway; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        
        cd backend
        
        # Create railway.json
        cat > railway.json << EOF
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
  }
}
EOF
        
        railway login
        railway init
        
        railway variables set MONGODB_URL="$MONGODB_URL"
        railway variables set DATABASE_NAME="rideswift_db"
        railway variables set SECRET_KEY="$(openssl rand -hex 32)"
        railway variables set BACKEND_CORS_ORIGINS="[\"$FRONTEND_URL\"]"
        railway variables set ENVIRONMENT="production"
        
        railway up
        
        echo -e "\n${GREEN}✅ Backend deployed!${NC}"
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${BLUE}Need help? Check DEPLOYMENT.md for detailed instructions${NC}"
