import dotenv

import auth.hasher
dotenv.load_dotenv()

from fastapi import FastAPI, Form
from typing import Annotated
import uvicorn as uv
import auth
import auth.utils
from auth.router import router as AuthRouter

app = FastAPI()
app.include_router(AuthRouter)

@app.get("/")
def hello_world():
    return "Hello World"

@app.post("/hash")
def hash_text(pt: Annotated[str, Form()]):
    return auth.hasher.get_password_hash(pt)

if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")