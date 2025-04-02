import dotenv
import auth.hasher
from fastapi import FastAPI, Form
from typing import Annotated
import uvicorn as uv
import auth
import auth.utils
from auth.router import router as AuthRouter
from services.chat import router as ChatRouter
from services.upload import router as UploadRouter
from services.chat_history import router as ChatHistoryRouter
from services.files import router as FilesRouter
from config import get_settings

dotenv.load_dotenv()

app = FastAPI()
app.include_router(AuthRouter)
app.include_router(ChatRouter)
app.include_router(UploadRouter)
app.include_router(ChatHistoryRouter)
app.include_router(FilesRouter)

settings = get_settings()

@app.get("/")
def hello_world():
    return "Hello World"


@app.post("/hash")
def hash_text(pt: Annotated[str, Form()]):
    return auth.hasher.get_password_hash(pt)


if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")
