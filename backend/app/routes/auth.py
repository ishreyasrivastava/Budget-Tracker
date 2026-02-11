"""
Authentication routes for user signup, login, and session management.
Uses Supabase Auth for secure authentication.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from ..models import UserSignUp, UserSignIn, AuthResponse, UserResponse
from ..database import supabase
from ..auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignUp):
    """
    Register a new user account.
    Creates user in Supabase Auth with optional metadata.
    """
    try:
        # Create user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name
                }
            }
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        user = response.user
        session = response.session
        
        # If email confirmation is required, session might be None
        if not session:
            return AuthResponse(
                user=UserResponse(
                    id=user.id,
                    email=user.email,
                    full_name=user.user_metadata.get("full_name") if user.user_metadata else None,
                    created_at=str(user.created_at)
                ),
                access_token="",  # Empty until email confirmed
                refresh_token="",
                token_type="bearer"
            )
        
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.user_metadata.get("full_name") if user.user_metadata else None,
                created_at=str(user.created_at)
            ),
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type="bearer"
        )
        
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {error_msg}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserSignIn):
    """
    Authenticate user and return access tokens.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = response.user
        session = response.session
        
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.user_metadata.get("full_name") if user.user_metadata else None,
                created_at=str(user.created_at)
            ),
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Sign out the current user (invalidates token on Supabase side).
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        # Even if signout fails server-side, client should clear tokens
        return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name")
    )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    """
    try:
        response = supabase.auth.refresh_session(refresh_token)
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )
