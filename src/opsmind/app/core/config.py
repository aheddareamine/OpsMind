from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    token_expiry: int = Field(ge=0, le=50)
    secret: int = Field(ge=20)
    database_url: str = Field(min_length=10, max_length=20) 
    password: str = Field(min_length=10, max_length=20)
    
    model_config = {
        "env_file": "./../../../.env",
        "env_file_encoding": "utf-8",
        }
