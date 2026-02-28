# Quick Start Guide

Get the StockSphere Trading Backend running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check PostgreSQL
psql --version

# Check Redis
redis-cli ping
```

## Quick Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Setup Database

```sql
-- In PostgreSQL
CREATE DATABASE stocksphere;
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://user:password@localhost:5432/stocksphere
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Start Server

```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

## First API Calls

### 1. Create a Zerodha Account

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

### 2. Get Marketwatch

```bash
curl http://localhost:8000/api/v1/marketwatch?symbols=RELIANCE&exchange=NSE
```

### 3. Place a Trade

```bash
curl -X POST http://localhost:8000/api/v1/trades \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "side": "BUY",
    "quantity": 10,
    "order_type": "REGULAR",
    "product": "INTRADAY",
    "price_type": "LIMIT",
    "price": 2500.50
  }'
```

### 4. Check Trade Status

```bash
# Use trade_id from previous response
curl http://localhost:8000/api/v1/trades/{trade_id}
```

## Next Steps

1. **Read Documentation:**
   - `README.md` - Overview
   - `SETUP.md` - Detailed setup
   - `ARCHITECTURE.md` - System design
   - `API_EXAMPLES.md` - API examples

2. **Integrate Real Broker APIs:**
   - See `IMPLEMENTATION_STATUS.md`
   - Replace mock implementations in adapters

3. **Connect Frontend:**
   - Update frontend API base URL
   - Test integration

## Troubleshooting

**Database connection error?**
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in `.env`

**Redis connection error?**
- Check Redis is running: `redis-cli ping`
- Verify REDIS_HOST/REDIS_PORT in `.env`

**Import errors?**
- Activate virtual environment
- Reinstall: `pip install -r requirements.txt`

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database.py          # DB setup
│   ├── models/              # Database models
│   ├── schemas/             # Request/response schemas
│   ├── services/            # Business logic
│   ├── adapters/            # Broker adapters
│   ├── api/routes/          # API endpoints
│   └── utils/               # Utilities
├── scripts/                 # DB scripts
├── requirements.txt         # Dependencies
└── *.md                     # Documentation
```

## Support

- Check `IMPLEMENTATION_STATUS.md` for what's implemented
- Review `ARCHITECTURE.md` for system design
- See `API_EXAMPLES.md` for detailed API usage
