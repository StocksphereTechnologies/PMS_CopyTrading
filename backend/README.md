# StockSphere Trading Backend

Multi-account trading backend supporting Zerodha (Kite Connect) and 5paisa APIs.

## Features

- **Multi-Account Management**: Add and manage multiple trading accounts
- **Marketwatch**: Fetch instruments and LTP from multiple brokers
- **Parallel Trade Execution**: Execute trades simultaneously across all enabled accounts
- **Broker Adapter Pattern**: Clean abstraction for broker APIs
- **Trade Ledger**: Track all trades and their execution results

## Tech Stack

- **Framework**: FastAPI (async)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for LTP caching
- **Brokers**: Zerodha Kite Connect, 5paisa API

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Update database URL, Redis settings, etc.

### 3. Setup Database

Create PostgreSQL database:

```sql
CREATE DATABASE stocksphere;
```

The application will create tables automatically on first run.

### 4. Start Redis

```bash
redis-server
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

## API Endpoints

### Accounts

- `POST /api/v1/accounts` - Create a new account
- `GET /api/v1/accounts` - List all accounts
- `GET /api/v1/accounts/{account_id}` - Get account details
- `PUT /api/v1/accounts/{account_id}` - Update account
- `DELETE /api/v1/accounts/{account_id}` - Delete account

### Marketwatch

- `GET /api/v1/marketwatch` - Get marketwatch data
  - Query params: `symbols` (optional), `exchange` (optional)

### Trades

- `POST /api/v1/trades` - Place a trade (executes in all enabled accounts)
- `GET /api/v1/trades/{trade_id}` - Get trade details

## Example Requests

### Create Account

```json
POST /api/v1/accounts
{
  "account_id": "ZERODHA_001",
  "broker_name": "ZERODHA",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret",
  "access_token": "your_access_token",
  "is_enabled": true
}
```

### Place Trade

```json
POST /api/v1/trades
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 10,
  "order_type": "REGULAR",
  "product": "INTRADAY",
  "price_type": "LIMIT",
  "price": 2500.50
}
```

### Get Marketwatch

```
GET /api/v1/marketwatch?symbols=RELIANCE&exchange=NSE
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   │   ├── account.py
│   │   └── trade.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── account.py
│   │   ├── trade.py
│   │   └── marketwatch.py
│   ├── services/            # Business logic
│   │   ├── account_service.py
│   │   ├── marketwatch_service.py
│   │   └── trade_orchestrator.py
│   ├── adapters/            # Broker adapters
│   │   ├── base.py
│   │   ├── zerodha_adapter.py
│   │   └── fivepaisa_adapter.py
│   ├── api/                 # API routes
│   │   └── routes/
│   │       ├── accounts.py
│   │       ├── marketwatch.py
│   │       └── trades.py
│   └── utils/               # Utilities
│       └── cache.py
├── requirements.txt
├── .env.example
└── README.md
```

## Notes

- Currently uses mock broker API calls. Replace mock implementations in adapters with actual API calls.
- Access tokens may need refresh logic - implement token refresh in adapters.
- Consider adding authentication/authorization middleware.
- Add rate limiting for broker API calls.
- Implement WebSocket for real-time marketwatch updates (optional).
