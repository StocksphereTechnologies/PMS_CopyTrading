# Setup Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- pip (Python package manager)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

#### Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE stocksphere;

-- Create user (optional)
CREATE USER stocksphere_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stocksphere TO stocksphere_user;
```

#### Update Database URL

Edit `.env` file:
```
DATABASE_URL=postgresql://stocksphere_user:your_password@localhost:5432/stocksphere
```

### 5. Setup Redis

#### Install Redis

**Windows:**
- Download from https://github.com/microsoftarchive/redis/releases
- Or use WSL: `sudo apt-get install redis-server`

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

#### Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

### 6. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stocksphere

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Broker API URLs
ZERODHA_API_BASE_URL=https://kite.zerodha.com
FIVEPAISA_API_BASE_URL=https://openapi.5paisa.com
```

### 7. Initialize Database

```bash
python scripts/init_db.py
```

Or the tables will be created automatically on first run.

### 8. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 9. Test the API

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Create an Account

```bash
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "ZERODHA_001",
    "broker_name": "ZERODHA",
    "api_key": "test_key",
    "api_secret": "test_secret",
    "access_token": "test_token",
    "is_enabled": true
  }'
```

#### Get Accounts

```bash
curl http://localhost:8000/api/v1/accounts
```

## Development Setup

### Using Docker (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: stocksphere
      POSTGRES_USER: stocksphere_user
      POSTGRES_PASSWORD: stocksphere_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up -d
```

Update `.env`:
```
DATABASE_URL=postgresql://stocksphere_user:stocksphere_pass@localhost:5432/stocksphere
```

## Troubleshooting

### Database Connection Error

- Verify PostgreSQL is running: `pg_isready`
- Check database URL in `.env`
- Ensure database exists: `psql -l | grep stocksphere`

### Redis Connection Error

- Verify Redis is running: `redis-cli ping`
- Check Redis host/port in `.env`
- Test connection: `redis-cli -h localhost -p 6379`

### Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

### Port Already in Use

- Change port: `uvicorn app.main:app --port 8001`
- Or kill process using port 8000

## Next Steps

1. Add your broker API credentials via `/api/v1/accounts`
2. Test marketwatch: `GET /api/v1/marketwatch`
3. Test trade execution: `POST /api/v1/trades`
4. Review `API_EXAMPLES.md` for detailed examples
5. Review `ARCHITECTURE.md` for system design
