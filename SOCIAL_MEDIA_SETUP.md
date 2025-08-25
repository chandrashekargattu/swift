# Social Media Integration Setup Guide

This guide will help you set up social media integrations for the RideSwift Interstate Cab Booking app.

## Overview

RideSwift now supports the following social media integrations:
- OAuth authentication (Login with Google, Facebook, Instagram, Twitter/X, LinkedIn)
- Social media sharing (Share bookings, referrals, and achievements)
- Instagram feed display
- Social ambassador program

## OAuth Setup

### 1. Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:3000/auth/google/callback`
5. Copy Client ID and Client Secret to `.env`:
   ```
   GOOGLE_OAUTH_CLIENT_ID=your-client-id
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
   ```

### 2. Facebook OAuth

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login product
4. Settings:
   - Valid OAuth Redirect URIs: `http://localhost:3000/auth/facebook/callback`
5. Copy App ID and App Secret to `.env`:
   ```
   FACEBOOK_APP_ID=your-app-id
   FACEBOOK_APP_SECRET=your-app-secret
   ```

### 3. Instagram OAuth

Instagram uses Facebook's infrastructure:

1. In your Facebook app, add Instagram Basic Display product
2. Configure Instagram Basic Display:
   - Valid OAuth Redirect URIs: `http://localhost:3000/auth/instagram/callback`
3. Copy Instagram App ID and App Secret to `.env`:
   ```
   INSTAGRAM_APP_ID=your-instagram-app-id
   INSTAGRAM_APP_SECRET=your-instagram-app-secret
   ```

### 4. Twitter/X OAuth

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Enable OAuth 2.0
4. Settings:
   - Type of App: Web App
   - Callback URI: `http://localhost:3000/auth/twitter/callback`
5. Copy API Key and API Secret to `.env`:
   ```
   TWITTER_API_KEY=your-api-key
   TWITTER_API_SECRET=your-api-secret
   ```

### 5. LinkedIn OAuth

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create a new app
3. Add OAuth 2.0 settings:
   - Redirect URLs: `http://localhost:3000/auth/linkedin/callback`
4. Copy Client ID and Client Secret to `.env`:
   ```
   LINKEDIN_CLIENT_ID=your-client-id
   LINKEDIN_CLIENT_SECRET=your-client-secret
   ```

## API Endpoints

### OAuth Endpoints

- `GET /api/v1/oauth/auth/{provider}` - Initiate OAuth flow
- `GET /api/v1/oauth/auth/{provider}/callback` - OAuth callback handler
- `POST /api/v1/oauth/connect/{provider}` - Connect social account to existing user
- `DELETE /api/v1/oauth/disconnect/{provider}` - Disconnect social account

### Social Sharing Endpoints

- `POST /api/v1/social/share/booking/{booking_id}` - Generate booking share links
- `POST /api/v1/social/share/referral` - Generate referral share links
- `POST /api/v1/social/share/achievement/{type}` - Generate achievement share links
- `GET /api/v1/social/instagram/feed` - Get Instagram feed posts
- `POST /api/v1/social/instagram/post` - Post to Instagram Business account
- `GET /api/v1/social/meta-tags` - Get social media meta tags

## Frontend Components

### Social Share Component

```tsx
import SocialShare from '@/components/social/SocialShare';

<SocialShare
  title="Join me on RideSwift!"
  description="Get 20% off your first ride"
  url="https://rideswift.com/ref/ABC123"
/>
```

### Instagram Feed Component

```tsx
import InstagramFeed from '@/components/social/InstagramFeed';

<InstagramFeed 
  username="rideswift" 
  limit={12} 
/>
```

## Features Implemented

### 1. Social Login
- Users can sign up/sign in using their social media accounts
- Automatic account creation for new OAuth users
- Account linking for existing users

### 2. Social Sharing
- Share bookings on social media
- Referral program with trackable links
- Achievement sharing (milestones, eco-warrior, social butterfly)
- Pre-formatted share content with hashtags

### 3. Instagram Integration
- Display Instagram feed in the app
- Responsive grid layout
- Hover effects showing likes and comments
- Direct links to Instagram posts

### 4. Social Page
- Dedicated `/social` page showcasing all social features
- Instagram feed display
- Share & earn section
- Social ambassador program information

## Production Deployment

For production deployment:

1. Update all OAuth redirect URIs to your production domain
2. Enable HTTPS for all OAuth callbacks
3. Update CORS settings in backend
4. Set proper environment variables
5. Configure social media meta tags for better sharing

## Testing

1. Test OAuth flows:
   ```bash
   # Click social login buttons on /signin page
   # Should redirect to provider and back
   ```

2. Test sharing:
   ```bash
   # Visit /social page
   # Click share buttons
   # Verify share links open correctly
   ```

3. Test Instagram feed:
   ```bash
   # Visit /social page
   # Check Instagram tab
   # Verify feed displays (currently mock data)
   ```

## Future Enhancements

1. Real Instagram API integration for live feed
2. Social media posting capabilities
3. Analytics for social shares
4. Influencer dashboard
5. Social media contests and campaigns
6. WhatsApp Business API integration
7. Social proof widgets (recent bookings, reviews)

## Troubleshooting

### OAuth Not Working
- Check API keys are correctly set in `.env`
- Verify redirect URIs match exactly
- Check browser console for errors
- Ensure backend is running

### Instagram Feed Not Loading
- Currently using mock data
- For real data, need Instagram Basic Display API setup
- Check CORS settings

### Share Links Not Opening
- Verify URLs are properly encoded
- Check if popup blockers are interfering
- Test in different browsers

## Support

For issues or questions about social media integration:
- Email: tech@rideswift.com
- Documentation: https://docs.rideswift.com/social-media
- API Reference: https://api.rideswift.com/docs
