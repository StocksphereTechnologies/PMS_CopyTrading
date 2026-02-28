# API Examples

This document provides example request/response payloads for all API endpoints.

## Base URL

```
http://localhost:8000/api/v1
```

## Accounts API

### 1. Create Account

**Request:**
```http
POST /accounts
Content-Type: application/json

{
  "account_id": "ZERODHA_001",
  "broker_name": "ZERODHA",
  "api_key": "your_api_key_here",
  "api_secret": "your_api_secret_here",
  "access_token": "your_access_token_here",
  "is_enabled": true
}
```

**Response:**
```json
{
  "id": 1,
  "account_id": "ZERODHA_001",
  "broker_name": "ZERODHA",
  "is_enabled": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### 2. Create 5paisa Account

**Request:**
```http
POST /accounts
Content-Type: application/json

{
  "account_id": "FIVEPAISA_001",
  "broker_name": "FIVEPAISA",
  "api_key": "your_5paisa_api_key",
  "api_secret": "your_5paisa_api_secret",
  "access_token": "your_5paisa_access_token",
  "is_enabled": true
}
```

### 3. Get All Accounts

**Request:**
```http
GET /accounts
```

**Response:**
```json
[
  {
    "id": 1,
    "account_id": "ZERODHA_001",
    "broker_name": "ZERODHA",
    "is_enabled": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  },
  {
    "id": 2,
    "account_id": "FIVEPAISA_001",
    "broker_name": "FIVEPAISA",
    "is_enabled": true,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": null
  }
]
```

### 4. Get Enabled Accounts Only

**Request:**
```http
GET /accounts?enabled_only=true
```

### 5. Get Account by ID

**Request:**
```http
GET /accounts/1
```

**Response:**
```json
{
  "id": 1,
  "account_id": "ZERODHA_001",
  "broker_name": "ZERODHA",
  "is_enabled": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### 6. Update Account

**Request:**
```http
PUT /accounts/1
Content-Type: application/json

{
  "is_enabled": false,
  "access_token": "new_access_token"
}
```

**Response:**
```json
{
  "id": 1,
  "account_id": "ZERODHA_001",
  "broker_name": "ZERODHA",
  "is_enabled": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### 7. Delete Account

**Request:**
```http
DELETE /accounts/1
```

**Response:**
```
204 No Content
```

## Marketwatch API

### 1. Get Marketwatch (All Instruments)

**Request:**
```http
GET /marketwatch
```

**Response:**
```json
{
  "items": [
    {
      "symbol": "RELIANCE",
      "exchange": "NSE",
      "ltp": 2500.50,
      "change": 50.25,
      "change_percent": 2.05,
      "volume": 1020000,
      "open": 2450.00,
      "high": 2510.00,
      "low": 2445.00,
      "prev_close": 2450.25
    },
    {
      "symbol": "TCS",
      "exchange": "NSE",
      "ltp": 3450.75,
      "change": -25.50,
      "change_percent": -0.73,
      "volume": 850000,
      "open": 3476.00,
      "high": 3480.00,
      "low": 3445.00,
      "prev_close": 3476.25
    }
  ],
  "count": 2
}
```

### 2. Get Marketwatch for Specific Symbols

**Request:**
```http
GET /marketwatch?symbols=RELIANCE&symbols=TCS&exchange=NSE
```

**Response:**
```json
{
  "items": [
    {
      "symbol": "RELIANCE",
      "exchange": "NSE",
      "ltp": 2500.50,
      "change": 50.25,
      "change_percent": 2.05,
      "prev_close": 2450.25
    },
    {
      "symbol": "TCS",
      "exchange": "NSE",
      "ltp": 3450.75,
      "change": -25.50,
      "change_percent": -0.73,
      "prev_close": 3476.25
    }
  ],
  "count": 2
}
```

### 3. Get Marketwatch Filtered by Exchange

**Request:**
```http
GET /marketwatch?exchange=NSE
```

## Trades API

### 1. Place Trade (Regular Limit Order)

**Request:**
```http
POST /trades
Content-Type: application/json

{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 10,
  "order_type": "REGULAR",
  "product": "INTRADAY",
  "price_type": "LIMIT",
  "price": 2500.50,
  "time_in_force": "DAY"
}
```

**Response:**
```json
{
  "trade_id": "550e8400-e29b-41d4-a716-446655440000",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 10,
  "order_type": "REGULAR",
  "product": "INTRADAY",
  "price_type": "LIMIT",
  "price": 2500.50,
  "trigger_price": null,
  "created_at": "2024-01-15T12:00:00Z",
  "executions": [
    {
      "account_id": "ZERODHA_001",
      "broker_name": "ZERODHA",
      "broker_order_id": "ZERODHA_RELIANCE_10",
      "status": "COMPLETED",
      "executed_price": null,
      "executed_quantity": 10,
      "error_reason": null
    },
    {
      "account_id": "FIVEPAISA_001",
      "broker_name": "FIVEPAISA",
      "broker_order_id": "FIVEPAISA_RELIANCE_10",
      "status": "COMPLETED",
      "executed_price": null,
      "executed_quantity": 10,
      "error_reason": null
    }
  ]
}
```

### 2. Place Market Order

**Request:**
```http
POST /trades
Content-Type: application/json

{
  "symbol": "TCS",
  "exchange": "NSE",
  "side": "SELL",
  "quantity": 5,
  "order_type": "REGULAR",
  "product": "INTRADAY",
  "price_type": "MARKET",
  "time_in_force": "IOC"
}
```

### 3. Place Stop Loss Order

**Request:**
```http
POST /trades
Content-Type: application/json

{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "side": "SELL",
  "quantity": 10,
  "order_type": "REGULAR",
  "product": "INTRADAY",
  "price_type": "STOP_LOSS",
  "price": 2480.00,
  "trigger_price": 2485.00
}
```

### 4. Place Bracket Order

**Request:**
```http
POST /trades
Content-Type: application/json

{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 10,
  "order_type": "BO",
  "product": "INTRADAY",
  "price_type": "LIMIT",
  "price": 2500.50,
  "target": 2550.00,
  "stoploss": 2480.00,
  "trailing_stoploss": 0
}
```

### 5. Place Cover Order

**Request:**
```http
POST /trades
Content-Type: application/json

{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 10,
  "order_type": "CO",
  "product": "INTRADAY",
  "price_type": "LIMIT",
  "price": 2500.50,
  "trigger_price": 2480.00
}
```

### 6. Get Trade Details

**Request:**
```http
GET /trades/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "trade_id": "550e8400-e29b-41d4-a716-446655440000",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 10,
  "order_type": "REGULAR",
  "product": "INTRADAY",
  "price_type": "LIMIT",
  "price": 2500.50,
  "trigger_price": null,
  "created_at": "2024-01-15T12:00:00Z",
  "executions": [
    {
      "account_id": "ZERODHA_001",
      "broker_name": "ZERODHA",
      "broker_order_id": "ZERODHA_RELIANCE_10",
      "status": "COMPLETED",
      "executed_price": 2500.50,
      "executed_quantity": 10,
      "error_reason": null
    },
    {
      "account_id": "FIVEPAISA_001",
      "broker_name": "FIVEPAISA",
      "broker_order_id": "FIVEPAISA_RELIANCE_10",
      "status": "FAILED",
      "executed_price": null,
      "executed_quantity": null,
      "error_reason": "Insufficient margin"
    }
  ]
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "broker_name must be either ZERODHA or FIVEPAISA"
}
```

### 404 Not Found

```json
{
  "detail": "Account with id 1 not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Error executing trade: No enabled accounts found"
}
```
