from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str

class UserWithId(User):
    id: int

class UserRegistration(User):
    password: str


class UserDBO(UserWithId):
    password_hash: str
