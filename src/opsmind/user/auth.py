from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import Select
import bcrypt

from opsmind.user.schema import UserResponse, UserCreate
from opsmind.user.model import User
from opsmind.core.config import get_settings
from opsmind.core.db import get_db


auth_router = APIRouter(prefix="/users")
settings = get_settings()


def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt()
    plain = plain.encode('utf-8')
    
    return bcrypt.hashpw(salt=salt, password=plain)


@auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.scalars(Select(User).where(User.email == user_in.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user_in.model_dump()
    user_data["hashed_password"] = hash_password(user_in.hashed_password)
    db_user = User(**user_data)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user