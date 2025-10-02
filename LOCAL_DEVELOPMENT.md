# Local Development Guide

Run the Dodo Payments Microservice directly on your local machine without Docker.

## 📋 Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **MySQL 8.0+** ([Download](https://dev.mysql.com/downloads/mysql/))
- **Git** (for cloning)
- **Dodo Payments Account** ([Sign up](https://dodopayments.com))

## 🚀 Quick Setup (5 Steps)

### Step 1: Install MySQL

#### macOS (Homebrew)
```bash
brew install mysql
brew services start mysql

# Secure installation (optional but recommended)
mysql_secure_installation
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure installation
sudo mysql_secure_installation
```

#### Windows
1. Download MySQL installer from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)
2. Run installer and follow wizard
3. Choose "Developer Default" setup
4. Set root password
5. Start MySQL service

### Step 2: Create Database

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE dodo_payments_db;

# Create user (optional but recommended)
CREATE USER 'payment_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON dodo_payments_db.* TO 'payment_user'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL
EXIT;
```

### Step 3: Initialize Database Schema

```bash
# Navigate to project directory
cd backend/payments-service

# Import schema
mysql -u payment_user -p dodo_payments_db < payments-db-structure.sql

# Or if using root:
mysql -u root -p dodo_payments_db < payments-db-structure.sql
```

### Step 4: Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Create .env file
cat > .env << 'EOF'
# Environment
ENVIRONMENT=development
SERVICE_PORT=8001
LOG_LEVEL=DEBUG

# Dodo Payments (REPLACE WITH YOUR KEYS)
DODO_API_KEY=your_dodo_api_key_here
DODO_WEBHOOK_SECRET=your_webhook_secret_here
DODO_BASE_URL=https://api.dodopayments.com

# Database
MYSQL_HOST=localhost
MYSQL_USER=payment_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=dodo_payments_db
MYSQL_PORT=3306

# Security
API_KEY_ENCRYPTION_KEY=local_dev_encryption_key_min_32_characters
WEBHOOK_SIGNING_SECRET=local_dev_webhook_signing_secret_key

# Features
ENABLE_REFUNDS=true
ENABLE_SUBSCRIPTIONS=true
ENABLE_ANALYTICS=true

# CORS (add your frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

# Edit .env with your actual values
nano .env  # or use any text editor
```

## ▶️ Run the Service

### Start Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the service
python main.py
```

You should see:
```
🚀 Starting Dodo Payments Microservice...
Environment: development
Port: 8001
✅ Database initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Alternative: Run with Uvicorn Directly

```bash
# More control over uvicorn settings
uvicorn main:app --host 0.0.0.0 --port 8001 --reload --log-level debug

# Or on specific host
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

**Options:**
- `--reload` - Auto-reload on code changes (development only)
- `--log-level debug` - Verbose logging
- `--workers 4` - Multiple workers (production)

## 🧪 Setup Sample Data

```bash
# In a new terminal (keep service running)
cd backend/payments-service
source venv/bin/activate

# Create sample app and products
python scripts/setup_sample_data.py
```

**Output:**
```
🚀 Setting up sample data...
✅ Created app:anikets-suppper-app
   App Secret: sk_anikets_app_xxxxx
✅ Created product: 10 Credits
✅ Created product: 50 Credits
✅ Created product: 100 Credits
...
```

## 🔑 Generate API Key

```bash
# Generate API key for your app
python scripts/generate_api_key.pyanikets-suppper-app
```

**Save the API key shown!** You'll need it for all API requests.

## ✅ Test the Service

### 1. Health Check

```bash
curl http://localhost:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": 1696156800.0,
  "environment": "development"
}
```

### 2. List Products

```bash
curl http://localhost:8001/products/anikets-suppper-app\
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

### 3. Create Checkout Session

```bash
curl -X POST http://localhost:8001/payments/checkout \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "app_name": "anikets-suppper-app",
    "user_id": "test_user_123",
    "product_id": "credits_50",
    "customer_email": "test@example.com"
  }'
```

### 4. View API Documentation

Open browser: **http://localhost:8001/docs**

## 🛠️ Development Workflow

### Hot Reload (Auto-restart on code changes)

```bash
# Run with --reload flag
uvicorn main:app --reload --port 8001
```

Now when you edit any `.py` file, the server automatically restarts!

### Debug Mode

```bash
# Set LOG_LEVEL=DEBUG in .env
echo "LOG_LEVEL=DEBUG" >> .env

# Run service
python main.py
```

### Using Python Debugger

Add breakpoints in your code:

```python
# In any file, e.g., routers/payments.py
def create_checkout(...):
    import pdb; pdb.set_trace()  # Debugger will stop here
    ...
```

### VS Code Debug Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--port",
        "8001"
      ],
      "jinja": true,
      "justMyCode": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

Press F5 to start debugging!

### PyCharm Debug Configuration

1. **Run → Edit Configurations**
2. **Add New Configuration → Python**
3. **Script path:** Select `main.py`
4. **Working directory:** `backend/payments-service`
5. **Environment variables:** Copy from `.env`
6. Click **OK** and run with Debug (Shift+F9)

## 🗄️ Database Management

### View Database

```bash
# Connect to MySQL
mysql -u payment_user -p dodo_payments_db

# Show tables
SHOW TABLES;

# View apps
SELECT * FROM app_registry;

# View products
SELECT * FROM product_catalog;

# View checkout sessions
SELECT * FROM checkout_sessions ORDER BY created_at DESC LIMIT 10;

# View payments
SELECT * FROM payments ORDER BY created_at DESC LIMIT 10;

# View user credits
SELECT * FROM user_credits;

# Exit
EXIT;
```

### Reset Database

```bash
# Drop and recreate
mysql -u payment_user -p -e "DROP DATABASE IF EXISTS dodo_payments_db; CREATE DATABASE dodo_payments_db;"

# Re-import schema
mysql -u payment_user -p dodo_payments_db < payments-db-structure.sql

# Re-setup sample data
python scripts/setup_sample_data.py
```

### MySQL GUI Tools

#### phpMyAdmin
```bash
# macOS
brew install phpmyadmin

# Ubuntu
sudo apt install phpmyadmin
```

#### MySQL Workbench
Download from [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)

#### DBeaver (Free & Cross-platform)
Download from [DBeaver](https://dbeaver.io/)

## 📊 Monitoring & Logs

### View Logs

Logs are printed to console by default. To save to file:

```bash
# Run and save logs
python main.py 2>&1 | tee logs/app.log

# Or with uvicorn
uvicorn main:app --reload --log-config logging_config.json
```

### Monitor MySQL Queries

```bash
# Enable MySQL query log
mysql -u root -p

SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/tmp/mysql-query.log';

# View logs
tail -f /tmp/mysql-query.log
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies (if you have pytest)
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pip install pytest-cov
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Manual Testing with cURL

```bash
# Save this as test.sh
#!/bin/bash

API_KEY="YOUR_API_KEY"
BASE_URL="http://localhost:8001"

echo "Testing health endpoint..."
curl $BASE_URL/health

echo "\nTesting products endpoint..."
curl $BASE_URL/products/anikets-suppper-app-H "X-API-Key: $API_KEY"

echo "\nTesting checkout endpoint..."
curl -X POST $BASE_URL/payments/checkout \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "app_name": "anikets-suppper-app",
    "user_id": "test_user",
    "product_id": "credits_50",
    "customer_email": "test@example.com"
  }'
```

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8001
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn main:app --port 8002
```

### MySQL Connection Failed

```bash
# Check MySQL is running
brew services list | grep mysql  # macOS
systemctl status mysql  # Linux
sc query MySQL80  # Windows

# Test connection
mysql -u payment_user -p -h localhost

# Check credentials in .env match MySQL
```

### Module Not Found

```bash
# Make sure virtual environment is activated
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Import Errors

```bash
# Run from project root
cd backend/payments-service
python main.py

# Or add to PYTHONPATH
export PYTHONPATH=/path/to/payments-service:$PYTHONPATH
```

## 📦 Installing Additional Tools

### Code Formatting

```bash
pip install black isort flake8

# Format code
black .
isort .
flake8 .
```

### Database Migrations

```bash
pip install alembic

# Initialize alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

## 🔄 Update Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade fastapi

# Freeze new versions
pip freeze > requirements.txt
```

## 🚀 Production Tips

### Environment-Specific Settings

```bash
# Create production .env
cp .env .env.production

# Edit for production
nano .env.production
```

### Run with Gunicorn (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# With auto-restart
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --reload
```

### Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Create ecosystem.config.js
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: "payment-service",
    script: "venv/bin/uvicorn",
    args: "main:app --host 0.0.0.0 --port 8001",
    cwd: "/path/to/payments-service",
    instances: 4,
    exec_mode: "cluster",
    watch: false,
    env: {
      ENVIRONMENT: "production"
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js

# Monitor
pm2 monit

# Logs
pm2 logs payment-service
```

## 📚 Next Steps

1. **Explore API Docs**: http://localhost:8001/docs
3. **Integrate with Your App**: See [README.md](README.md)
4. **Deploy**: See [Docker](docker-compose.yml) or cloud guides

## 🆘 Getting Help

- **Documentation**: [README.md](README.md)
- **Issues**: Create GitHub issue
- **Logs**: Check console output
- **Database**: Check MySQL logs

---

**Happy Local Development! 🎉**

