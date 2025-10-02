# Project Structure - Dodo Payments Microservice

## 📁 Directory Layout

```
payments-service/
├── 📄 main.py                      # FastAPI application entry point
├── 📄 config.py                    # Configuration management
├── 📄 database.py                  # SQLAlchemy models & DB connection
├── 📄 requirements.txt             # Python dependencies
├── 📄 Dockerfile                   # Docker container definition
├── 📄 docker-compose.yml           # Multi-container setup
├── 📄 .gitignore                   # Git ignore rules
├── 📄 .dockerignore                # Docker ignore rules
│
├── 📚 Documentation/
│   ├── README.md                   # Complete project documentation
│   ├── QUICKSTART.md               # 5-minute setup guide
│   └── PROJECT_STRUCTURE.md        # This file
│
├── 🔧 Database/
│   └── payments-db-structure.sql   # MySQL schema & sample data
│
├── 🛣️ routers/                      # API route handlers
│   ├── __init__.py
│   ├── payments.py                 # Checkout, webhook, verify
│   ├── products.py                 # Product catalog
│   ├── credits.py                  # Credit management
│   └── apps.py                     # App registration (admin)
│
├── 🔧 services/                     # Business logic
│   ├── __init__.py
│   ├── dodo_service.py             # Dodo Payments API wrapper
│   ├── credit_service.py           # Credit operations
│   └── webhook_service.py          # Webhook processing
│
├── 🔐 middleware/                   # Request middleware
│   ├── __init__.py
│   └── auth.py                     # API key authentication
│
└── 📜 scripts/                      # Utility scripts
    ├── __init__.py
    ├── setup_sample_data.py        # Populate test data
    └── generate_api_key.py         # Generate API keys
```

## 📄 File Descriptions

### Core Application Files

#### `main.py`
- FastAPI application initialization
- Router registration
- Middleware setup
- Global exception handling
- Lifespan events (startup/shutdown)

#### `config.py`
- Pydantic settings management
- Environment variable loading
- Configuration validation
- Helper properties (database URL, CORS origins)

#### `database.py`
- SQLAlchemy ORM models
- Database connection setup
- Session management
- Enums for status types
- Database initialization

#### `requirements.txt`
```txt
fastapi==0.109.0          # Web framework
uvicorn==0.27.0           # ASGI server
dodopayments==1.53.5      # Dodo Payments SDK
pymysql==1.1.0            # MySQL driver
sqlalchemy==2.0.25        # ORM
pydantic-settings==2.1.0  # Config management
httpx==0.26.0             # Async HTTP client
```

## 🛣️ API Routers

### `routers/payments.py`
**Endpoints:**
- `POST /payments/checkout` - Create Dodo checkout session
- `GET /payments/verify/{identifier}` - Verify payment status (accepts payment_id or subscription_id)
- `POST /payments/webhook` - Handle Dodo webhooks (via Svix)

**Key Functions:**
- `create_checkout()` - Validates app/product, creates Dodo session with return_url
- `verify_payment()` - Returns payment status by payment_id or subscription_id
- `handle_webhook()` - Processes payment events with Svix signature verification
- `_handle_payment_success()` - Credits user, calls app callback
- `_handle_subscription_renewed()` - Creates subscription payment record

### `routers/products.py`
**Endpoints:**
- `GET /products/{app_name}` - List products for app
- `GET /products/{app_name}/{product_id}` - Get product details

**Features:**
- Active/inactive filtering
- API key authentication required

### `routers/credits.py`
**Endpoints:**
- `GET /credits/{app_name}/{user_id}` - Get credit balance
- `POST /credits/deduct` - Deduct credits
- `GET /credits/{app_name}/{user_id}/transactions` - Transaction history

**Use Cases:**
- Apps call `/deduct` when user uses features
- Users check balance via their app

### `routers/apps.py`
**Endpoints:**
- `POST /apps/register` - Register new app
- `GET /apps/{app_name}` - Get app info
- `PUT /apps/{app_name}/activate` - Activate app
- `PUT /apps/{app_name}/deactivate` - Deactivate app

**Security:**
- Should be admin-only in production
- Generates API keys & app secrets

## 🔧 Services Layer

### `services/dodo_service.py`
**DodoPaymentsService** class wraps Dodo API:
- `create_checkout_session()` - Create payment session
- `verify_webhook_signature()` - Validate webhooks
- `get_payment_details()` - Fetch payment info
- `create_refund()` - Process refunds
- `cancel_subscription()` - Cancel subscriptions

### `services/credit_service.py`
**CreditService** class manages credits:
- `get_or_create_user_credits()` - Initialize user
- `add_credits()` - Add credits (purchase)
- `deduct_credits()` - Remove credits (usage)
- `refund_credits()` - Reverse credits
- `get_balance()` - Check balance
- `get_transaction_history()` - Audit trail

### `services/webhook_service.py`
**WebhookService** class handles events:
- `log_webhook_event()` - Record incoming webhooks
- `mark_event_processing()` - Update status
- `mark_event_processed()` - Complete processing
- `mark_event_failed()` - Log errors
- `send_app_callback()` - Notify apps
- `_generate_signature()` - Sign callbacks

## 🔐 Middleware

### `middleware/auth.py`
**API Key Authentication:**
- `verify_api_key()` - Validates X-API-Key header
- `get_current_app_name()` - FastAPI dependency
- Checks key active status & expiration
- Updates last_used_at timestamp

## 📜 Utility Scripts

### `scripts/setup_sample_data.py`
Creates test data:
- Registers "anikets-suppper-app" app
- Creates 5 sample products
- Can be run multiple times (idempotent)

Usage:
```bash
python scripts/setup_sample_data.py
```

### `scripts/generate_api_key.py`
Generates API key for app:
- Creates secure random key
- Stores in database
- Outputs key to console

Usage:
```bash
python scripts/generate_api_key.pyanikets-suppper-app
```

## 🐳 Docker Files

### `Dockerfile`
Multi-stage build:
- Base: Python 3.11 slim
- Installs MySQL client libraries
- Creates non-root user
- Health check endpoint
- Runs on port 8001

### `docker-compose.yml`
Services:
1. **payment-service**
   - FastAPI application
   - Port 8001
   - Depends on payment-db

2. **payment-db**
   - MySQL 8.0
   - Port 3307 (external)
   - Auto-initializes schema
   - Persistent volume

## 🗄️ Database Schema

### Core Tables (11 total)
1. `app_registry` - Apps using service
2. `product_catalog` - Products per app
3. `checkout_sessions` - Dodo sessions
4. `payments` - Completed payments
5. `webhook_events` - Event log
6. `subscriptions` - Active subscriptions
7. `user_credits` - Credit balances
8. `credit_transactions` - Transaction log
9. `refunds` - Refund records
10. `api_keys` - Authentication
11. `analytics_summary` - Daily metrics

See `payments-db-structure.sql` for full schema.

## 🔄 Request Flow

### Checkout Flow
```
1. App Backend → POST /payments/checkout
   ├─ Headers: X-API-Key
   └─ Body: {app_name, user_id, product_id}

2. Payment Service
   ├─ Validates API key → auth.py
   ├─ Checks app & product → database.py
   ├─ Creates Dodo session → dodo_service.py
   └─ Saves checkout → CheckoutSession model

3. Response
   └─ {session_id, checkout_url, expires_at}

4. User completes payment on Dodo

5. Dodo → POST /payments/webhook
   ├─ Verify signature → dodo_service.py
   ├─ Log event → webhook_service.py
   ├─ Update payment → Payment model
   ├─ Add credits → credit_service.py
   └─ Callback app → webhook_service.py
```

## 🔒 Security Layers

1. **API Key Authentication** (`auth.py`)
   - Required on all protected endpoints
   - Validated against database
   - Tracks usage

2. **Webhook Signature Verification** (`dodo_service.py`)
   - HMAC-SHA256 signature
   - Prevents replay attacks

3. **Event Idempotency** (`webhook_service.py`)
   - Prevents duplicate processing
   - Uses unique event_id

4. **CORS** (`main.py`)
   - Configurable origins
   - Disabled in production

5. **HTTPS Only**
   - Enforced in production
   - Encrypted transport

## 📊 Monitoring Points

### Logs
- Request/response times (`main.py`)
- API key usage (`auth.py`)
- Webhook events (`webhook_service.py`)
- Payment processing (`payments.py`)

### Metrics
- `/health` - Service health
- Database connections
- Webhook processing time
- Payment success rate

### Database
- `webhook_events.status` - Processing status
- `api_keys.last_used_at` - API usage
- `analytics_summary` - Revenue metrics

## 🧪 Testing

### Manual Testing
1. Start services: `docker-compose up`
2. Setup data: `python scripts/setup_sample_data.py`
3. Generate key: `python scripts/generate_api_key.pyanikets-suppper-app`
4. Test API: `curl http://localhost:8001/health`

### Automated Testing
```bash
pytest                        # Run tests
pytest --cov                  # With coverage
pytest -v                     # Verbose
```

## 🚀 Deployment Options

### Docker (Recommended)
```bash
docker build -t dodo-payments:latest .
docker run -d -p 8001:8001 --env-file .env dodo-payments:latest
```

### AWS Lambda
- Use container image support
- Or Mangum adapter for API Gateway

### AWS ECS/Fargate
- Deploy as container
- Use RDS for MySQL
- Secrets Manager for credentials

### Kubernetes
- Deploy as deployment
- Use ConfigMap for config
- Use Secrets for credentials

## 📚 Dependencies Graph

```
main.py
  ├─ config.py (settings)
  ├─ database.py (models)
  ├─ routers/
  │   ├─ payments.py
  │   │   ├─ services/dodo_service.py
  │   │   ├─ services/credit_service.py
  │   │   └─ services/webhook_service.py
  │   ├─ products.py
  │   ├─ credits.py
  │   │   └─ services/credit_service.py
  │   └─ apps.py
  └─ middleware/auth.py
```

## 🔄 Development Workflow

1. **Make changes** to code
2. **Test locally**: `python main.py`
3. **Test in Docker**: `docker-compose up --build`
4. **Check logs**: `docker-compose logs -f`
5. **Run tests**: `pytest`
6. **Commit changes**: `git commit`
7. **Deploy**: Build & push container

## 📦 Build Artifacts

### Production
- Docker image: `dodo-payments:latest`
- Database dump: `payments-db-structure.sql`
- Environment template: `.env.example`

### Documentation
- API docs (Swagger): `/docs`
- ReDoc: `/redoc`
- README.md
- QUICKSTART.md

---

**Last Updated**: October 1, 2025  
**Version**: 1.0.0  
**Python**: 3.11+  
**FastAPI**: 0.109.0  
**MySQL**: 8.0

