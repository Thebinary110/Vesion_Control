from fastapi import APIRouter, Depends , HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas.user import UserCreate, UserResponse
from utils.security import hash_password
from utils.security import verify_password
from utils.jwt import create_access_token
from schemas.auth import LoginRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login_user(credentials: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
           data={"user_id": user.id}
        )


    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
