from .core.config import Settings

from fastapi import FastAPI
from pydantic import BaseModel, Field

S = Settings()

class Product(BaseModel):
    price: int = Field(ge=10, le=20)
    name: str = Field(min_length= 5, max_length= 25)

app = FastAPI()

@app.get("/")
def hy():
    return {'salut' : 'Hello World'}

@app.post("/", status_code=201)
def ingesting(product: Product):
    return {'product_name': product.name, 'product_price': product.price}

@app.get("/api/v1/health")
def health_metric():
    return {'status': 'ok'}
