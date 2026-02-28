"""
User Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserSignup(BaseModel):
    """User signup request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field("India", max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('phone_number')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not re.match(r'^\+?[0-9\-\s()]+$', v):
            raise ValueError('Invalid phone number format')
        return v


class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema (without password)"""
    user_id: int
    email: str
    full_name: str
    phone_number: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithToken(UserResponse):
    """User response with access token"""
    access_token: str
    token_type: str = "bearer"


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None
