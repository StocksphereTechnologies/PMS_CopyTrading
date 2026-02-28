# Installing Playwright for Zerodha Auto-Login

## Quick Setup

After installing Python dependencies, you need to install Playwright browsers:

```bash
# Install Playwright browsers (Chromium)
playwright install chromium

# Or install all browsers
playwright install
```

## What This Does

Playwright is used for headless browser automation to:
1. Open Zerodha's Kite Connect login page
2. Automatically fill in credentials (user ID, password, TOTP)
3. Extract `request_token` from the redirect URL
4. Exchange it for `access_token` via Kite Connect API

## Troubleshooting

If you see errors like "Playwright not installed":
1. Make sure `playwright` Python package is installed: `pip install playwright`
2. Run `playwright install chromium` to download the browser
3. Restart your backend server

## Alternative: Manual Token Entry

If Playwright doesn't work, you can manually get the `request_token`:

1. Open browser: `https://kite.trade/connect/login?api_key=YOUR_API_KEY&v=3`
2. Login with your credentials
3. Copy the `request_token` from the redirect URL
4. Use the API endpoint: `POST /api/v1/zerodha/accounts/{id}/request-token` with the token
