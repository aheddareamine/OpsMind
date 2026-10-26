from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Select
from pydantic import EmailStr
from passlib.context import CryptContext

from opsmind.core.db import get_db
from opsmind.user.schema import UserResponse, UserCreate
from opsmind.user.model import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

app = FastAPI()

@app.get("/")
def hy():
    return {"salut": "Welcome Home :)"}


@app.post("/user", response_model=UserResponse)
def add_user(user_in : UserCreate, db : Session = Depends(get_db)):
    existing_duplicate = db.scalars(Select(User).where(User.email == user_in.email)).first()
    if existing_duplicate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="duplicated email")

    db_user = User(**user_in.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/{user_email}")
def get_user_by_email(user_email: EmailStr, db : Session = Depends(get_db)):
    user = db.scalars(Select(User).where(User.email == user_email)).first()
    return user


@app.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
 
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user