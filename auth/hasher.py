from passlib.context import CryptContext

# To get these config options run
# docker run -it --entrypoint kratos oryd/kratos:v0.5 hashers argon2 calibrate 1s

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__parallelism=16,
    argon2__memory_cost=2097152,
    argon2__rounds=1,
    argon2__digest_size=32,
)

def verify_password(plaintext: str, hashed_password: str):
    return pwd_context.verify(plaintext, hashed_password)


def get_password_hash(pwd: str):
    return pwd_context.hash(pwd)