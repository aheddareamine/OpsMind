from pydantic import BaseModel, EmailStr, ConfigDict


class User(BaseModel):
    email : EmailStr
    username : str
    age : int


class UserCreate(User):
    hashed_password : str


class UserResponse(User):
    model_config = ConfigDict(from_attributes=True)