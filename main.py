from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Select
from pydantic import EmailStr

from opsmind.core.db import get_db
from opsmind.user.schema import UserCreate
from opsmind.user.model import User
from opsmind.user.auth import auth_router


app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def hy():
    return {"salut": "Welcome Home :)"}


@app.get("/{user_email}")
def get_user_by_email(user_email: EmailStr, db : Session = Depends(get_db)):
    user = db.scalars(Select(User).where(User.email == user_email)).first()
    return user
