# 🚀 Quick Production Environment Setup

## ⚡ **Fast Setup (3 Steps)**

### **Step 1: Run the Setup Script**
```bash
# From your project root
python setup_production_env.py
```

This will:
- ✅ Create `Backend/.env.production`
- ✅ Create `frontend/.env.production`
- ✅ Generate a secure SECRET_KEY automatically

### **Step 2: Edit Backend Production File**
```bash
# Edit backend production environment
nano Backend/.env.production
```

**Key variables to update:**
- `GOOGLE_CLIENT_ID` - Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Your Google OAuth client secret
- `GOOGLE_REDIRECT_URI` - Your Railway domain (after deployment)
- `FRONTEND_URL` - Your Vercel domain (after deployment)
- `STRIPE_SECRET_KEY` - Your production Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` - Your production Stripe publishable key

### **Step 3: Edit Frontend Production File**
```bash
# Edit frontend production environment
nano frontend/.env.production
```

**Key variables to update:**
- `REACT_APP_API_URL` - Your Railway backend domain (after deployment)
- `REACT_APP_GOOGLE_CLIENT_ID` - Same as backend
- `REACT_APP_STRIPE_PUBLISHABLE_KEY` - Your production Stripe publishable key

## 🔄 **Alternative Manual Setup**

If you prefer to do it manually:

### **Backend Production**
```bash
cd Backend
cp env.production.ready .env.production
# Edit .env.production with your values
```

### **Frontend Production**
```bash
cd frontend
cp env.production.ready .env.production
# Edit .env.production with your values
```

## 📋 **What Gets Created**

After running the setup script, you'll have:

```
mail_merge_kit/
├── Backend/
│   ├── .env.production          # ← Production backend variables
│   ├── env.production.ready     # Template (keep for reference)
│   └── env.production.txt       # Original template
├── frontend/
│   ├── .env.production          # ← Production frontend variables
│   ├── env.production.ready     # Template (keep for reference)
│   └── env.production.txt       # Original template
├── setup_production_env.py      # Setup script
└── QUICK_SETUP.md               # This file
```

## 🎯 **Production Deployment Flow**

1. **Run setup script** → Creates production .env files
2. **Edit .env.production files** → Add your actual credentials
3. **Deploy to Railway** → Backend with production variables
4. **Deploy to Vercel** → Frontend with production variables
5. **Update URLs** → Replace placeholders with actual domains

## 🚨 **Important Notes**

- **Never commit** `.env.production` files to Git
- **Keep templates** for future reference
- **Update URLs** after getting your actual domains
- **Use production keys** for Stripe (not test keys)
- **Same Google OAuth credentials** for both environments
