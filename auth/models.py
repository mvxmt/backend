from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

class UserRegistration(User):
    password: str
    
class UserDBO(User):
    password_hash: str

