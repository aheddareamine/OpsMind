from pydantic import BaseModel, EmailStr, ConfigDict


class TokenData(BaseModel):
    token : str | None = None


class User(BaseModel):
    email : EmailStr


class UserCreate(User):
    password : str
    username : str
    is_admin : bool


class UserResponse(User):
    username : str
    is_admin : bool
    model_config = ConfigDict(from_attributes=True)