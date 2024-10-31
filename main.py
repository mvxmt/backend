from fastapi import FastAPI, Form
from typing import Annotated
import uvicorn as uv
import auth
import dotenv

import auth.utils

dotenv.load_dotenv()

app = FastAPI()

@app.get("/")
def hello_world():
    return "Hello World"

@app.post("/hash")
def hash_text(pt: Annotated[str, Form()]):
    return auth.utils.get_password_hash(pt)

if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")