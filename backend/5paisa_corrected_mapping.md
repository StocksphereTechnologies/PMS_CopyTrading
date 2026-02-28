# 5paisa Dashboard Fields - CORRECTED MAPPING

## What You See on Dashboard

Based on your dashboard, you have these fields:

1. **API Key** - Your application key
2. **Encryption Key** - Secret key for encryption
3. **User ID** - ⚠️ **THIS IS DIFFERENT FROM CLIENT CODE!**
4. **App Source** - Usually "10074"
5. **User Password** - Your MPIN

## CORRECTED Mapping

| Dashboard Field | Database Field | Code Variable | Example Value |
|----------------|----------------|---------------|---------------|
| **API Key** | `api_key` | `APP_NAME` | `Sq7vHjWitc...` |
| **Encryption Key** | `api_secret` | `ENCRYPTION_KEY` | `zELHPHbI6W...` |
| **User ID** (from dashboard) | `user_key` | `USER_KEY` | ⚠️ **NOT 50350228!** |
| **App Source** | `app_source` | `APP_SOURCE` | `10074` |
| **User Password** | `encrypted_password` | `PASSWORD` | Your MPIN |
| Client Code (login ID) | `trading_login_id` | `USER_ID` | `50350228` |

## The Key Issue

**USER_KEY should be the "User ID" from dashboard, NOT the Client Code (50350228)!**

This is why you're getting "Invalid Vendor UserID" - we've been setting:
```python
user_key = "50350228"  # ❌ WRONG - This is Client Code
```

It should be:
```python
user_key = "THE_USER_ID_FROM_DASHBOARD"  # ✅ CORRECT
```

## What to Do

1. **Look at your 5paisa dashboard**
2. **Find the "User ID" field** (it's separate from Client Code)
3. **Copy that User ID value**
4. **Run the recreate script again** and paste the correct User ID when prompted

The "User ID" from dashboard is likely another alphanumeric string (similar to API Key format), NOT the client code 50350228.
