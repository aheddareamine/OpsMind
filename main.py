from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Select

from opsmind.core.db import get_db
from opsmind.user.schema import UserResponse, UserCreate
from opsmind.user.model import User


app = FastAPI()

@app.get("/")
def hy():
    return {"salut": "Welcome Home :)"}


@app.post("/user", response_model=UserResponse)
def add_user(user_in : UserCreate, db : Session = Depends(get_db)):
    db_user = User(**user_in.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh()
    return db_user


# @app.get("/{user_id}")
# def get_user(user_id: str, db : Session = Depends(get_db) ):
#     user = Select(User)