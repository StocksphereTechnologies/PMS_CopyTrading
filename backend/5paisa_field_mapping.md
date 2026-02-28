# 5paisa Credentials Mapping

## From 5paisa Dashboard → Database Fields

Based on what you see in your 5paisa dashboard, here's the exact mapping:

| 5paisa Dashboard Field | Database Field | Field in Code | Notes |
|------------------------|----------------|---------------|-------|
| **API Key** | `api_key` | `APP_NAME` | Main API identifier |
| **Encryption Key** | `api_secret` | `ENCRYPTION_KEY` | Secret key for encryption |
| **User ID** | `trading_login_id` | `USER_ID` | Your client code (50350228) |
| **App Source** | `app_source` | `APP_SOURCE` | Usually "10074" |
| **User Password** | `encrypted_password` | `PASSWORD` | Your MPIN/Trading PIN |

## Additional Fields

| Field | Database Field | Value | Notes |
|-------|----------------|-------|-------|
| **USER_KEY** | `user_key` | Same as API Key | For py5paisa, USER_KEY = API Key |
| **TOTP Secret** | `encrypted_totp_secret` | From authenticator app | Base32 secret from QR code |

---

## Exact Mapping for Your Code

```python
cred = {
    "APP_NAME": account.api_key,              # ← API Key from dashboard
    "APP_SOURCE": account.app_source,         # ← App Source from dashboard (10074)
    "USER_ID": account.trading_login_id,      # ← User ID from dashboard (50350228)
    "PASSWORD": decrypted_password,           # ← User Password from dashboard (MPIN)
    "USER_KEY": account.user_key,             # ← Same as API Key
    "ENCRYPTION_KEY": account.api_secret      # ← Encryption Key from dashboard
}
```

---

## What to Update in Your Database

You need to ensure these fields in the `accounts` table for your 5paisa account:

1. **`api_key`** = Copy "API Key" from dashboard
2. **`api_secret`** = Copy "Encryption Key" from dashboard  
3. **`user_key`** = Copy "API Key" from dashboard (same as api_key)
4. **`app_source`** = Copy "App Source" from dashboard (probably "10074")
5. **`trading_login_id`** = Your User ID (50350228)
6. **`encrypted_password`** = Your User Password (MPIN) - encrypted
7. **`encrypted_totp_secret`** = Your TOTP secret - encrypted

---

## Quick Update Script

Here's how to update your database with the correct values from the dashboard:

```python
# Update 5paisa account credentials
from app.core.database import AsyncSessionLocal
from app.models.account import Account, BrokerName
from app.core.encryption import encryption_service
from sqlalchemy import select

async def update_5paisa_creds():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Account).where(Account.broker_name == BrokerName.FIVEPAISA.value)
        )
        account = result.scalar_one_or_none()
        
        if account:
            # Copy these values from your 5paisa dashboard
            api_key = "PASTE_API_KEY_HERE"           # From dashboard
            encryption_key = "PASTE_ENCRYPTION_KEY_HERE"  # From dashboard
            app_source = "PASTE_APP_SOURCE_HERE"     # Usually "10074"
            
            # Update account
            account.api_key = api_key
            account.api_secret = encryption_key
            account.user_key = api_key  # Same as api_key
            account.app_source = app_source
            
            await db.commit()
            print("✅ Credentials updated!")
```

---

## Verification

After updating, your credentials should look like:
- `api_key`: Long alphanumeric string (e.g., "Sq7vHjWitckkHmpGQWKw8eHBg0MOn1eN")
- `api_secret`: Long alphanumeric string (Encryption Key)
- `user_key`: Same as api_key
- `app_source`: "10074" (or whatever dashboard shows)
- `trading_login_id`: "50350228"

**IMPORTANT**: Make sure you copy the values EXACTLY as shown in the dashboard, with no extra spaces or characters.
