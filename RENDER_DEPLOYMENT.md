# 🚀 Free Deployment Guide: Render + Vercel

## 💰 **Why Render Instead of Railway?**

- **✅ Completely FREE** - 750 hours/month (enough for 24/7)
- **✅ PostgreSQL database included** - No extra costs
- **✅ Auto-deploy from GitHub** - Same as Railway
- **✅ Custom domains** - Free SSL included
- **✅ No credit card required** - Truly free

## 🎯 **Deployment Steps**

### **Step 1: Deploy Backend to Render**

1. **Go to [Render.com](https://render.com)**
   - Sign up with GitHub (free)
   - Create a new account

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `mail_merge_kit` repository

3. **Configure Service:**
   - **Name:** `mail-merge-backend`
   - **Root Directory:** `Backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app_db:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

4. **Set Environment Variables:**
   - Go to "Environment" tab
   - Add these variables (copy from your `.env.production`):
     ```
           GOOGLE_CLIENT_ID=your_google_client_id_here
      GOOGLE_CLIENT_SECRET=your_google_client_secret_here
     GOOGLE_REDIRECT_URI=https://your-backend-name.onrender.com/auth/google/callback
     FRONTEND_URL=https://your-frontend-domain.vercel.app
     MAX_FREE_USERS=20
     STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here
     STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key_here
     STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
     EMAIL_USER=ywork.parry@gmail.com
     EMAIL_PASSWORD=veprhckdygvlzdzp
     EMAIL_HOST=smtp.gmail.com
     EMAIL_PORT=587
     FLASK_ENV=production
     SECRET_KEY=your-generated-secret-key
     ```

5. **Create Database:**
   - Go to "New +" → "PostgreSQL"
   - **Name:** `mail-merge-db`
   - **Database:** `mailmerge`
   - **User:** `mailmerge`
   - **Plan:** Free

6. **Link Database to Service:**
   - Go back to your web service
   - In "Environment" tab, add:
     ```
     DATABASE_URL=postgresql://mailmerge:password@host:port/mailmerge
     ```
   - Render will provide the actual connection string

7. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your Render domain: `https://your-app-name.onrender.com`

### **Step 2: Deploy Frontend to Vercel (Still Free)**

1. **Go to [Vercel.com](https://vercel.com)**
   - Sign up with GitHub
   - Import your repository

2. **Configure Build:**
   - **Framework Preset:** `Create React App`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

3. **Set Environment Variables:**
   ```
   REACT_APP_API_URL=https://your-backend-name.onrender.com
   REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here
   REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key_here
   ```

4. **Deploy:**
   - Click "Deploy"
   - Note your Vercel domain: `https://your-app-name.vercel.app`

### **Step 3: Update URLs and Google OAuth**

1. **Update Backend Environment:**
   - Go to Render → Your service → Environment
   - Update `GOOGLE_REDIRECT_URI` with your Render domain
   - Update `FRONTEND_URL` with your Vercel domain

2. **Update Frontend Environment:**
   - Go to Vercel → Settings → Environment Variables
   - Update `REACT_APP_API_URL` with your Render backend URL

3. **Update Google OAuth:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Add your Render domain to authorized redirect URIs:
     ```
     https://your-backend-name.onrender.com/auth/google/callback
     ```
   - Add your Vercel domain to authorized JavaScript origins:
     ```
     https://your-frontend-name.vercel.app
     ```

## 🎉 **You're Done!**

- **Backend:** `https://your-app-name.onrender.com` (FREE)
- **Frontend:** `https://your-app-name.vercel.app` (FREE)
- **Database:** PostgreSQL included (FREE)

## 💡 **Pro Tips:**

1. **Render free tier:** 750 hours/month = 31.25 days (enough for 24/7)
2. **Auto-sleep:** Service sleeps after 15 minutes of inactivity
3. **Wake up:** First request after sleep takes 30-60 seconds
4. **Custom domain:** You can add your own domain later

## 🚨 **Important Notes:**

- **Never commit** `.env` files to Git
- **Use production keys** for Stripe (not test keys)
- **Update Google OAuth** with both domains
- **Test thoroughly** after deployment

Ready to deploy? Start with Render backend first! 🚀
