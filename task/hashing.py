from passlib.context import CryptContext
"""
    For the password hashing we used the Hash,
    and for the verify the password we use verify.
"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)