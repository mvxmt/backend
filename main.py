import dotenv
import auth.hasher
from fastapi import FastAPI, Form
from typing import Annotated
import uvicorn as uv
import auth
import auth.utils
from auth.router import router as AuthRouter
from services.chat import router as ChatRouter
from config import get_settings

dotenv.load_dotenv()

app = FastAPI()
app.include_router(AuthRouter)
app.include_router(ChatRouter)

settings = get_settings()

@app.get("/")
def hello_world():
    return "Hello World"


@app.post("/hash")
def hash_text(pt: Annotated[str, Form()]):
    return auth.hasher.get_password_hash(pt)


if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")
