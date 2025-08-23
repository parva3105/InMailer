# User Limit System

This application now includes a user limit system that restricts free access to the first 50 users who sign up.

## How It Works

### 1. **User Limit Configuration**
- Default limit: **50 free users**
- Configurable via environment variable: `MAX_FREE_USERS`
- Set in your `.env` file or environment

### 2. **Registration Process**
- New users can only sign up if under the limit
- Existing users can always sign in (no retroactive restrictions)
- Google OAuth automatically checks the limit before creating new accounts

### 3. **Limit Enforcement**
- **During OAuth**: New user creation is blocked if limit reached
- **API Response**: Returns 403 status with clear error message
- **Logging**: All limit checks are logged for monitoring

## Configuration

### Environment Variables
```bash
# Set in your .env file
MAX_FREE_USERS=50
```

### Changing the Limit
1. Update `MAX_FREE_USERS` in your environment
2. Restart the application
3. The new limit takes effect immediately

## Monitoring

### Check Current Status
```bash
# Run the monitoring script
python check_user_limit.py

# Or call the API endpoint
GET /api/user-limit-status
```

### Admin Endpoint
```bash
# View all users (for monitoring)
GET /api/admin/users
```

## API Endpoints

### 1. **User Limit Status**
```
GET /api/user-limit-status
```
**Response:**
```json
{
  "current_users": 25,
  "max_users": 50,
  "is_registration_open": true,
  "remaining_slots": 25,
  "message": "Open for registration - 25/50 users"
}
```

### 2. **Admin Users List**
```
GET /api/admin/users
```
**Response:**
```json
{
  "total_users": 25,
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "is_google_user": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

## Error Handling

### Limit Reached Response
When a new user tries to register after the limit is reached:

```json
{
  "error": "Sorry! We have reached our limit of 50 free users. Please contact us for premium access.",
  "user_limit_reached": true,
  "current_users": 50,
  "max_users": 50
}
```

**HTTP Status:** 403 Forbidden

## Business Logic

### Free Tier (First 50 Users)
- ✅ Full access to all features
- ✅ Unlimited templates
- ✅ Unlimited email sends
- ✅ No restrictions

### After Limit Reached
- ❌ New registrations blocked
- ❌ Clear upgrade messaging
- ✅ Existing users unaffected

## Future Enhancements

### Premium Tier Implementation
1. **Payment Integration**: Stripe, PayPal, etc.
2. **User Roles**: Free vs Premium users
3. **Feature Gating**: Limit features for free users
4. **Upgrade Flow**: Seamless transition to premium

### Advanced Limits
1. **Time-based Limits**: Monthly quotas
2. **Feature Limits**: Template count, email volume
3. **Tiered Pricing**: Multiple premium levels

## Deployment Considerations

### Environment Variables
- Set `MAX_FREE_USERS` in production
- Use different limits for staging/testing
- Monitor user growth

### Database Monitoring
- Track user creation rates
- Monitor when limit approaches
- Plan for premium tier launch

### User Communication
- Clear messaging about limits
- Upgrade path information
- Contact details for premium access

## Testing

### Local Testing
```bash
# Set a low limit for testing
export MAX_FREE_USERS=3

# Run the application
python app_db.py

# Check status
python check_user_limit.py
```

### Limit Testing
1. Set `MAX_FREE_USERS=2`
2. Create 2 test users
3. Try to create a 3rd user
4. Verify limit enforcement works

## Security Notes

- Admin endpoints are currently unprotected
- In production, add proper authentication
- Consider rate limiting for status checks
- Log all limit-related activities
