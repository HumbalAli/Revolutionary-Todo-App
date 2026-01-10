from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ...auth import create_access_token, create_test_user
from ...database import get_session
from ...models.user import User

router = APIRouter()

class UserCreateRequest(BaseModel):
    email: str
    name: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/auth/register", response_model=AuthResponse)
async def register_user(
    user_data: UserCreateRequest,
    session: Session = Depends(get_session)
):
    """Create a new user and return JWT token for testing"""
    try:
        # Check if user already exists
        from sqlmodel import select
        statement = select(User).where(User.email == user_data.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            user = existing_user
        else:
            # Create new user
            user = User(
                email=user_data.email,
                name=user_data.name
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        # Create access token
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

from ...auth import get_current_user

# Get current user info
@router.get("/auth/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
    }


# Also add a test endpoint
@router.get("/auth/test")
async def test_auth(current_user: User = Depends(lambda: None)):  # Mock dependency for testing
    """Test endpoint for development"""
    return {"message": "Auth test endpoint working"}