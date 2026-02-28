"""
User model for multi-user authentication
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """User model with authentication and profile information"""
    __tablename__ = "users"
    
    # Primary Key {this user id is not same as the broker user id}
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    
    
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True, index=True)
    
    
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India", nullable=True)
    
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, full_name={self.full_name}, is_active={self.is_active})>"
