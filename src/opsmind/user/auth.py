from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from opsmind.user.exceptions import credentials_exception
from uuid import UUID, uuid4
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

def create_access_token(id: str):
    to_encode = {"jti": str(uuid4()), "sub": id, "token_type": "access"}
    access_expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode["exp"] = access_expire

    access_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return access_token


def create_refresh_token(id: str):
    to_encode = {"jti": str(uuid4()), "sub": id, "token_type": "refresh"}
    refresh_expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode["exp"] = refresh_expire
    
    refresh_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    return refresh_token


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            options={"require": ["exp", "sub", "token_type"]}, 
            algorithms=[settings.algorithm])
        if payload['token_type'] != "access":
            raise InvalidTokenError
            
        user_id = UUID(payload["sub"])
    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception()

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_exception()

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
def sign_in(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form_data.username))

    if not user:
        verify_password(form_data.password, DUMMY_HASH)
        raise HTTPException(status_code=400, detail="Wrong Credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong Credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/users/refresh",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
        )

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/refresh", status_code=status.HTTP_200_OK)
def create_access_tokens(request: Request, db: Session = Depends(get_db)):
    try:
        refresh_token = request.cookies.get("refresh_token")

        if refresh_token is None:
            raise credentials_exception()
        refresh_payload = jwt.decode(
            refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub", "token_type"]}
            )

        user_id = UUID(refresh_payload['sub'])
        if db.scalar(select(User).where(User.id == user_id)) is None\
            or refresh_payload['token_type'] != 'refresh':
            raise credentials_exception()

    except (ValueError, KeyError, InvalidTokenError):
        raise credentials_exception()

    access_token = create_access_token(refresh_payload['sub'])

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserResponse)
def read_me(user: User = Depends(get_current_user)):
    return user