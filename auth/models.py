from pydantic import BaseModel

class UserDBO(BaseModel):
    email: str
    hashed_password: str