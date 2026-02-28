# Architecture Overview

## System Architecture

The StockSphere Trading Backend follows a clean, modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                    │
│                      (app/main.py)                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Routes Layer                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Accounts │  │ Marketwatch  │  │    Trades    │           │
│  └──────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Account    │  │ Marketwatch  │  │    Trade     │       │
│  │   Service    │  │   Service    │  │ Orchestrator │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Adapter Layer                            │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   Zerodha    │  │  FivePaisa   │                         │
│  │   Adapter    │  │   Adapter    │                         │
│  └──────────────┘  └──────────────┘                         │
│         │                    │                              │
│         └────────┬───────────┘                              │
│                  ▼                                          │
│         BrokerInterface (ABC)                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Zerodha    │  │  5paisa API  │  │    Redis     │    │
│  │ Kite Connect │  │              │  │    Cache     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐         │
│  │ Accounts │  │  Trades  │  │ TradeExecutions │         │
│  └──────────┘  └──────────┘  └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Models Layer (`app/models/`)

**Account Model:**
- Stores trading account credentials
- Fields: `account_id`, `broker_name`, `api_key`, `api_secret`, `access_token`, `is_enabled`

**Trade Model:**
- Represents a single trade request from the UI
- One trade can have multiple executions (one per account)
- Fields: `trade_id`, `symbol`, `exchange`, `side`, `quantity`, `order_type`, etc.

**TradeExecution Model:**
- Stores execution result for each account
- Links to both Trade and Account
- Fields: `broker_order_id`, `status`, `executed_price`, `error_reason`

### 2. Schemas Layer (`app/schemas/`)

Pydantic models for request/response validation:
- `AccountCreate`, `AccountUpdate`, `AccountResponse`
- `TradeRequest`, `TradeResponse`, `TradeExecutionResponse`
- `MarketWatchItem`, `MarketWatchResponse`

### 3. Service Layer (`app/services/`)

**AccountService:**
- CRUD operations for accounts
- Account validation and management

**MarketWatchService:**
- Fetches instruments from all enabled accounts
- Aggregates LTP data
- Caches LTP using Redis (5-second TTL)
- Normalizes symbols across brokers

**TradeOrchestrator:**
- Receives single trade request
- Fetches all enabled accounts
- Executes trades in parallel using `asyncio.gather()`
- Handles failures gracefully (one failure doesn't stop others)
- Saves execution results to database

### 4. Adapter Layer (`app/adapters/`)

**BrokerInterface (ABC):**
- Abstract base class defining broker contract
- Methods: `get_instruments()`, `get_ltp()`, `place_order()`, `normalize_symbol()`

**ZerodhaAdapter:**
- Implements BrokerInterface for Zerodha Kite Connect API
- Maps our order types to Zerodha format
- Handles Zerodha-specific symbol normalization

**FivePaisaAdapter:**
- Implements BrokerInterface for 5paisa API
- Maps our order types to 5paisa format
- Handles 5paisa-specific symbol normalization

### 5. API Routes (`app/api/routes/`)

**Accounts Routes:**
- `POST /accounts` - Create account
- `GET /accounts` - List accounts
- `GET /accounts/{id}` - Get account
- `PUT /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Delete account

**Marketwatch Routes:**
- `GET /marketwatch` - Get marketwatch data

**Trades Routes:**
- `POST /trades` - Place trade (executes in all enabled accounts)
- `GET /trades/{trade_id}` - Get trade details

## Data Flow

### Trade Execution Flow

```
1. Frontend sends POST /trades with trade request
   ↓
2. TradeOrchestrator.execute_trade() receives request
   ↓
3. Creates Trade record in database
   ↓
4. Fetches all enabled accounts
   ↓
5. Creates async tasks for each account
   ↓
6. Executes all tasks in parallel using asyncio.gather()
   ↓
7. Each adapter.place_order() calls broker API
   ↓
8. Results collected (success or failure)
   ↓
9. TradeExecution records created for each account
   ↓
10. Database committed
    ↓
11. Response returned with all execution results
```

### Marketwatch Flow

```
1. Frontend requests GET /marketwatch?symbols=RELIANCE
   ↓
2. MarketWatchService.get_marketwatch() called
   ↓
3. Checks Redis cache for LTP
   ↓
4. If not cached, fetches from all enabled accounts
   ↓
5. Each adapter.get_ltp() called in parallel
   ↓
6. Aggregates results (average if multiple)
   ↓
7. Caches result in Redis (5 seconds)
   ↓
8. Returns marketwatch items
```

## Design Patterns

### 1. Adapter Pattern
- Broker-specific implementations abstracted behind `BrokerInterface`
- Easy to add new brokers by implementing the interface
- Isolates broker-specific logic

### 2. Service Layer Pattern
- Business logic separated from API routes
- Services are reusable and testable
- Clear separation of concerns

### 3. Repository Pattern (via SQLAlchemy)
- Database access abstracted through models
- Easy to swap database implementations

### 4. Dependency Injection
- FastAPI's dependency system for database sessions
- Services injected into routes

## Parallel Execution

Trade execution uses Python's `asyncio.gather()` for true parallel execution:

```python
execution_tasks = [
    TradeOrchestrator._execute_single_account(account, trade_request)
    for account in accounts
]

execution_results = await asyncio.gather(*execution_tasks, return_exceptions=True)
```

- All accounts execute simultaneously
- `return_exceptions=True` ensures one failure doesn't stop others
- Results collected and saved to database

## Error Handling

- **Account-level errors**: Captured per account, stored in `TradeExecution.error_reason`
- **Trade-level errors**: Returned as HTTP error responses
- **Broker API errors**: Handled in adapters, returned as execution failures

## Caching Strategy

- **LTP Cache**: Redis with 5-second TTL
- **Cache Key Format**: `ltp:{exchange}:{symbol}`
- **Cache Invalidation**: Automatic expiration

## Security Considerations

1. **API Keys**: Stored encrypted in database (implement encryption layer)
2. **Access Tokens**: Should be refreshed periodically
3. **CORS**: Configured for specific origins
4. **Input Validation**: Pydantic schemas validate all inputs

## Future Enhancements

1. **WebSocket Support**: Real-time marketwatch updates
2. **Token Refresh**: Automatic access token refresh
3. **Rate Limiting**: Per-broker rate limiting
4. **Order Status Polling**: Background jobs to update order status
5. **Authentication**: JWT-based authentication
6. **Logging**: Structured logging with correlation IDs
7. **Monitoring**: Metrics and health checks
8. **Testing**: Unit and integration tests
