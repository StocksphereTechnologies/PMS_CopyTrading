# Zerodha Auto-Login Setup Guide

## Overview

The backend now supports **fully automated Zerodha login** using Playwright headless browser automation. This eliminates the need for manual token entry on every restart.

## How It Works

1. **On Backend Startup**: For each enabled Zerodha account:
   - Checks if `access_token` exists and is valid
   - If missing or expired, automatically:
     - Opens Zerodha Kite Connect login page in headless browser
     - Fills in credentials (user ID, password, TOTP)
     - Extracts `request_token` from redirect URL
     - Exchanges it for `access_token` via Kite Connect API
     - Saves `access_token` to database

2. **WebSocket Connection**: Only starts after valid `access_token` is confirmed

## Setup Steps

### 1. Install Playwright Browser

After installing Python dependencies, install the Chromium browser:

```bash
playwright install chromium
```

### 2. Add Zerodha Account

Use the `/api/v1/accounts` endpoint with your Zerodha credentials:

```json
{
  "broker_name": "ZERODHA",
  "trading_login_id": "YOUR_USER_ID",
  "trading_password": "YOUR_PASSWORD",
  "totp_secret_key": "YOUR_TOTP_SECRET",
  "api_key": "YOUR_KITE_API_KEY",
  "api_secret": "YOUR_KITE_API_SECRET",
  "nickname": "My Zerodha Account",
  "is_enabled": true
}
```

**Important**: 
- `totp_secret_key` should be your Base32-encoded TOTP secret (from your authenticator app)
- `api_key` and `api_secret` come from your Kite Connect app (https://developers.kite.trade)

### 3. Restart Backend

On startup, the backend will:
- ✅ Automatically log in to Zerodha
- ✅ Generate and save `access_token`
- ✅ Start WebSocket connection for real-time market data

## Troubleshooting

### Playwright Not Installed

If you see: `Playwright not installed. Install with: pip install playwright && playwright install chromium`

**Fix**:
```bash
pip install playwright
playwright install chromium
```

### Login Fails

If automated login fails, check:

1. **Credentials are correct**: Verify `trading_login_id`, `trading_password`, `totp_secret_key`
2. **TOTP Secret is valid**: Must be Base32-encoded (e.g., `JBSWY3DPEHPK3PXP`)
3. **API Key/Secret are correct**: From your Kite Connect app settings
4. **Network connectivity**: Backend can reach `kite.trade` and `kite.zerodha.com`

### Manual Token Entry (Fallback)

If automated login doesn't work, you can manually get the `request_token`:

1. Open browser: `https://kite.trade/connect/login?api_key=YOUR_API_KEY&v=3`
2. Login with your credentials
3. Copy the `request_token` from the redirect URL
4. Call: `POST /api/v1/zerodha/accounts/{account_id}/request-token`

```json
{
  "request_token": "YOUR_REQUEST_TOKEN"
}
```

## Logs

Watch for these log messages:

- ✅ `Starting automated Zerodha login for account X`
- ✅ `Successfully extracted request_token`
- ✅ `Successfully generated access_token`
- ✅ `Starting Zerodha WebSocket for account X`
- ✅ `Zerodha WebSocket connected`

If you see errors:
- ❌ `Cannot start Zerodha WebSocket: no valid access_token` → Login failed
- ❌ `Could not extract request_token` → Check credentials
- ❌ `WebSocket connection upgrade failed (400)` → Invalid or expired token

## Security Notes

- All credentials are encrypted in the database using Fernet encryption
- TOTP secrets are never logged
- Access tokens expire daily and are automatically refreshed
