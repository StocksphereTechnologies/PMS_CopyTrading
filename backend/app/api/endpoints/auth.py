"""
Authentication endpoints: signup, login, get user
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserSignup, UserLogin, UserResponse, UserWithToken, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignup,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: Valid email address (unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit, special char)
    - **full_name**: User's full name
    - **phone_number**: Optional phone number
    - **address, city, state, country**: Optional address fields
    """
    
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    
    hashed_password = get_password_hash(user_data.password)
    
    
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        address=user_data.address,
        city=user_data.city,
        state=user_data.state,
        country=user_data.country,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email} (ID: {new_user.user_id})")
    
    
    access_token = create_access_token(
        data={"user_id": new_user.user_id, "email": new_user.email}
    )
    
    
    return UserWithToken(
        user_id=new_user.user_id,
        email=new_user.email,
        full_name=new_user.full_name,
        phone_number=new_user.phone_number,
        address=new_user.address,
        city=new_user.city,
        state=new_user.state,
        country=new_user.country,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/login", response_model=UserWithToken)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token valid for 7 days
    """
    
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    logger.info(f"User logged in: {user.email} (ID: {user.user_id})")
    
    # access token mf
    access_token = create_access_token(
        data={"user_id": user.user_id, "email": user.email}
    )
    
    
    return UserWithToken(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        address=user.address,
        city=user.city,
        state=user.state,
        country=user.country,
        is_active=user.is_active,
        created_at=user.created_at,
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile
    
    Requires: Authorization header with Bearer token
    """
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        address=current_user.address,
        city=current_user.city,
        state=current_user.state,
        country=current_user.country,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout():
    """
    Logout user (client-side token deletion)
    
    Note: JWT tokens are stateless, so logout is handled client-side by deleting the token
    """
    return {"message": "Successfully logged out. Please delete the token on client side."}
