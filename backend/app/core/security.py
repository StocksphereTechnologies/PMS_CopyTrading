"""
Security utilities for password hashing and JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
# Use settings from app.core.config
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use SECRET_KEY for JWT tokens from unified config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = getattr(settings, "ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

# necessary 
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token (e.g., {"user_id": 1, "email": "user@example.com"})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Increase duration to 7 days to be safe
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    print(f"DEBUG: Creating token with payload: {to_encode}", flush=True)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"DEBUG: Created token (first 10 chars): {encoded_jwt[:10]}...", flush=True)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        print(f"DEBUG: Attempting to decode token with key: {SECRET_KEY[:5]}...", flush=True)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"DEBUG: JWT Decode error in security.py: {str(e)}", flush=True)
        return None
