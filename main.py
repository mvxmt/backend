from fastapi import FastAPI
import uvicorn as uv

app = FastAPI()

@app.get("/")
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    uv.run(app)