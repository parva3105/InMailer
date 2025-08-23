# Payment System Setup Guide

This guide will help you set up the one-time $10 lifetime payment system for your Mail Merge Kit.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Stripe Account
1. Go to [stripe.com](https://stripe.com) and create an account
2. Get your API keys from the Stripe Dashboard
3. Add them to your `.env` file:

```bash
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 3. Run Database Migration
```bash
python db/migrate_payment_fields.py
```

### 4. Start Your Server
```bash
python app_db.py
```

## 🔧 Detailed Configuration

### Stripe Dashboard Setup

1. **Create a Product**:
   - Go to Products → Add Product
   - Name: "Lifetime Access to Mail Merge Kit"
   - Price: $10.00 USD
   - Billing: One-time

2. **Set Up Webhooks**:
   - Go to Developers → Webhooks
   - Add endpoint: `https://yourdomain.com/api/payment/webhook`
   - Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
   - Copy the webhook secret to your `.env` file

3. **Test Mode vs Live Mode**:
   - Use test keys for development
   - Switch to live keys for production
   - Test with Stripe's test card numbers

### Environment Variables

Copy `env_example.txt` to `.env` and fill in your values:

```bash
# Required for payments
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional: Custom price ID
STRIPE_LIFETIME_PRICE_ID=price_...
```

## 💳 Payment Flow

### 1. User clicks "Upgrade to Lifetime Access"
### 2. Frontend calls `/api/payment/checkout-session`
### 3. User is redirected to Stripe Checkout
### 4. After payment, Stripe sends webhook to `/api/payment/webhook`
### 5. User's account is upgraded to lifetime access

## 🔒 Security Features

- **Webhook Verification**: All Stripe webhooks are verified using signatures
- **User Authentication**: Payment endpoints require valid user sessions
- **Duplicate Prevention**: Users can't pay multiple times for lifetime access
- **Metadata Tracking**: All payments include user ID and email for tracking

## 📱 Frontend Integration

Your frontend can use these endpoints:

```javascript
// Create checkout session
const response = await fetch('/api/payment/checkout-session', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json'
  }
});

// Check payment status
const status = await fetch('/api/payment/status', {
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});
```

## 🧪 Testing

### Test Card Numbers
- **Success**: 4242 4242 4242 4242
- **Decline**: 4000 0000 0000 0002
- **3D Secure**: 4000 0025 0000 3155

### Test Mode
- All transactions are simulated
- No real charges
- Perfect for development and testing

## 🚀 Production Deployment

1. **Switch to Live Keys**:
   - Replace `sk_test_` with `sk_live_`
   - Replace `pk_test_` with `pk_live_`

2. **Update Webhook URL**:
   - Change from `localhost` to your production domain
   - Ensure HTTPS is enabled

3. **Monitor Transactions**:
   - Check Stripe Dashboard regularly
   - Set up email notifications for failed payments

## 💰 Pricing

- **One-time payment**: $10.00 USD
- **Lifetime access**: No recurring fees
- **All features included**: Unlimited templates, emails, and usage

## 🆘 Troubleshooting

### Common Issues

1. **Webhook not working**:
   - Check webhook secret in `.env`
   - Verify webhook URL is accessible
   - Check Stripe Dashboard for webhook failures

2. **Payment not updating user status**:
   - Check database migration ran successfully
   - Verify webhook is receiving events
   - Check server logs for errors

3. **Stripe API errors**:
   - Verify API keys are correct
   - Check if you're using test vs live keys
   - Ensure Stripe account is active

### Support

- Check Stripe documentation: [stripe.com/docs](https://stripe.com/docs)
- Review server logs for detailed error messages
- Test with Stripe's test mode first

## 🎯 Next Steps

1. Set up your Stripe account
2. Configure environment variables
3. Run database migration
4. Test payment flow
5. Deploy to production
6. Monitor transactions

Your payment system is now ready to handle unlimited users with the $10 lifetime access model! 🎉
