from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from uuid import UUID

import jwt

from opsmind.user.schema import UserResponse, UserCreate
from opsmind.user.model import User
from opsmind.core.config import get_settings
from opsmind.core.db import get_db


auth_router = APIRouter(prefix="/users")

settings = get_settings()

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword") # to prevent user enumeration using timing attacks 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/signin")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = UUID(payload["sub"])
    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception
        
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_exception

    return user


@auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def sign_up(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.scalars(select(User).where(User.email == user_in.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.scalars(select(User).where(User.username == user_in.username)).first():
        raise HTTPException(status_code=400, detail="Username already exist")

    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = get_password_hash(user_in.password)
    db_user = User(**user_data)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@auth_router.post("/signin", status_code=status.HTTP_200_OK)
def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form_data.username))
    
    if not user:
        verify_password(form_data.password, DUMMY_HASH)
        raise HTTPException(status_code=400, detail="Wrong Credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong Credentials")

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
