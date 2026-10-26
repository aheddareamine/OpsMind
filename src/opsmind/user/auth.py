from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from opsmind.core.config import get_settings
from opsmind.core.db import get_db


settings = get_settings()

auth_router = APIRouter(prefix="users")

@auth_router.post("/token")
def 