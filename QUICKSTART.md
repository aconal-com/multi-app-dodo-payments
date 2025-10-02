# Quick Start Guide - Dodo Payments Microservice

Get up and running in 5 minutes! 🚀

## 🚀 Two Ways to Run

### Option 1: Docker (Recommended) ⭐
- Easiest setup
- Includes MySQL automatically
- See instructions below

### Option 2: Local Development
- Run directly with Python
- Use your local MySQL
- Better for debugging
- **👉 See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for detailed guide**

---

## Docker Setup (Option 1)

### Prerequisites

- Docker & Docker Compose installed
- Dodo Payments account (sign up at https://dodopayments.com)

## Step 1: Get Your Dodo API Keys

1. Log into Dodo Payments dashboard
2. Navigate to API Keys section
3. Copy your:
   - API Key
   - Webhook Secret

## Step 2: Clone & Configure

```bash
cd backend/payments-service

# Create environment file
cat > .env << EOF
DODO_API_KEY=your_dodo_api_key_here
DODO_WEBHOOK_SECRET=your_webhook_secret_here
DODO_BASE_URL=https://api.dodopayments.com

# Keep these as-is for local development
ENVIRONMENT=development
SERVICE_PORT=8001
LOG_LEVEL=INFO

MYSQL_HOST=payment-db
MYSQL_USER=payment_user
MYSQL_PASSWORD=payment_password_123
MYSQL_DATABASE=dodo_payments_db
MYSQL_PORT=3306

API_KEY_ENCRYPTION_KEY=local_dev_encryption_key_min_32_chars
WEBHOOK_SIGNING_SECRET=local_dev_webhook_signing_secret

ENABLE_REFUNDS=true
ENABLE_SUBSCRIPTIONS=true
ENABLE_ANALYTICS=true

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF
```

## Step 3: Start Services

```bash
# Start all services (database + payment service)
docker-compose up -d

# View logs
docker-compose logs -f payment-service
```

Wait for message: `✅ Database initialized successfully`

## Step 4: Setup Sample Data

```bash
# This creates sample app and products
docker exec dodo-payments-service python scripts/setup_sample_data.py
```

You'll see output like:
```
✅ Created app:anikets-suppper-app
   App Secret: sk_anikets_app_xxxxx
✅ Created product: 10 Credits
✅ Created product: 50 Credits
...
```

## Step 5: Generate API Key

```bash
docker exec dodo-payments-service python scripts/generate_api_key.pyanikets-suppper-app
```

Save the API key shown - you'll need it for all requests!

## Step 6: Test It!

### Check Health
```bash
curl http://localhost:8001/health
```

### List Products
```bash
curl http://localhost:8001/products/anikets-suppper-app\
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

### Create Checkout
```bash
curl -X POST http://localhost:8001/payments/checkout \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "app_name": "anikets-suppper-app",
    "user_id": "test_user_123",
    "product_id": "credits_50",
    "customer_email": "test@example.com",
    "extra_data": {
      "return_url": "http://localhost:5173/payment/success"
    }
  }'
```

Response:
```json
{
  "session_id": "cks_xxxxx",
  "checkout_url": "https://checkout.dodopayments.com/xxxxx",
  "expires_at": "2025-10-02T10:00:00Z"
}
```

After payment, Dodo redirects to:
- One-time: `return_url?payment_id=pay_xxx&status=succeeded`
- Subscription: `return_url?subscription_id=sub_xxx&status=active`

### View API Docs
Open browser: http://localhost:8001/docs

## 🎉 You're Ready!

### Next Steps

1. **Integrate with your app:**
   - Use the API key in your backend
   - Call `/payments/checkout` when user wants to buy credits
   - Handle webhooks at your callback URL

2. **Add more products:**
   - POST to `/apps/register` with new app
   - Or update `scripts/setup_sample_data.py`

3. **Test payments:**
   - Use Dodo's test cards
   - Check webhook logs in `webhook_events` table

## Common Commands

```bash
# View logs
docker-compose logs -f payment-service

# Restart service
docker-compose restart payment-service

# Stop all
docker-compose down

# Stop and remove data
docker-compose down -v

# Access database
docker exec -it dodo-payments-db mysql -u payment_user -p
# Password: payment_password_123

# Check database
mysql> USE dodo_payments_db;
mysql> SELECT * FROM app_registry;
mysql> SELECT * FROM product_catalog;
mysql> SELECT * FROM checkout_sessions;
```

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs payment-service

# Common issue: Port already in use
# Change SERVICE_PORT in docker-compose.yml
```

### Can't connect to database
```bash
# Wait for DB to be ready
docker-compose logs payment-db

# Look for: "ready for connections"
```

### API key not working
```bash
# Generate new key
docker exec dodo-payments-service python scripts/generate_api_key.pyanikets-suppper-app

# Check key in database
docker exec -it dodo-payments-db mysql -u payment_user -p
mysql> SELECT * FROM api_keys WHERE is_active = 1;
```

## Production Deployment

See [README.md](./README.md) for production deployment guide.

## Support

- Full docs: [README.md](./README.md)
- API reference: http://localhost:8001/docs

Happy coding! 🚀

