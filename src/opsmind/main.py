from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hy():
    return {'salut' : 'Hello World'}