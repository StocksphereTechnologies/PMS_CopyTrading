# 5paisa Credentials - CORRECT MAPPING (from AutoTrader)

## AutoTrader Platform Form Fields

Based on the AutoTrader platform that successfully works with 5paisa:

| AutoTrader Form Field | What It Means | Our Database Field | Current Issue |
|----------------------|---------------|-------------------|---------------|
| **Trading Platform Login ID** | 5paisa Client Code | `trading_login_id` | ✅ Correct (50350228) |
| **MPIN** | 6-digit trading PIN | `encrypted_password` | ✅ Correct |
| **TOTP Key** | Authenticator secret | `encrypted_totp_secret` | ✅ Correct |
| **User Key (API)** | From API details | `user_key` | ⚠️ **ISSUE HERE** |
| **App Source (API)** | From API details | `app_source` | ✅ Correct (10074) |

## The Key Insight

AutoTrader uses **FP_API_TOTP** platform which means it's using the **same py5paisa library** we are!

The form shows:
- **User Key (API)** - This is a separate field from Login ID
- **App Source (API)** - This is from API details

## What We're Missing

Looking at our current setup vs AutoTrader:

### Our Current Config:
```python
cred = {
    "APP_NAME": api_key,           # ✅ Correct
    "APP_SOURCE": app_source,      # ✅ Correct  
    "USER_ID": trading_login_id,   # ✅ Correct (50350228)
    "PASSWORD": mpin,              # ✅ Correct
    "USER_KEY": ???,               # ❌ THIS IS THE PROBLEM
    "ENCRYPTION_KEY": api_secret   # ✅ Correct
}
```

### The Issue

We've been trying:
1. `USER_KEY = api_key` → "Invalid Vendor UserID"
2. `USER_KEY = "50350228"` → "Invalid Vendor UserID"  
3. `USER_KEY = dashboard_user_id` → "UserKey Not Found"

But AutoTrader's form has a **separate "User Key (API)" field**!

## What "User Key (API)" Actually Is

Based on AutoTrader's working implementation, the "User Key (API)" is likely:
1. **NOT** the API Key (APP_NAME)
2. **NOT** the Client Code (50350228)
3. **NOT** the "User ID" from dashboard
4. A **separate credential** from 5paisa API details

## Where to Find It

On your 5paisa dashboard, look for:
- Section: **API Details** or **Developer API**
- Look for a field specifically labeled: **"User Key"** or **"Vendor Key"**
- This might be different from "API Key" and "Encryption Key"

## Possible Scenarios

### Scenario 1: User Key = API Key (for individuals)
Some documentation says for individual users, User Key = API Key (VendorKey).
- We tried this → "Invalid Vendor UserID"

### Scenario 2: User Key is a separate field
There's a separate "User Key" field in API details that we haven't found yet.
- Need to check dashboard more carefully

### Scenario 3: User Key needs to be generated
Some APIs require you to "Generate User Key" separately from API Key.
- Check if there's a "Generate" button for User Key

## Next Steps

1. **Check your 5paisa dashboard API section** for:
   - API Key ✅ (we have this)
   - Encryption Key ✅ (we have this)
   - **User Key** ❓ (separate field?)
   - App Source ✅ (we have this)

2. **Look for these sections**:
   - Developer API
   - API Credentials
   - API Keys
   - Vendor Details

3. **Screenshot or list ALL fields** you see in the API section

## Why This Matters

AutoTrader successfully uses 5paisa with FP_API_TOTP, which means:
- ✅ The py5paisa library DOES work
- ✅ TOTP authentication DOES work
- ✅ There IS a correct configuration
- ❌ We're just missing the correct "User Key" value

The fact that AutoTrader works proves this is solvable!
