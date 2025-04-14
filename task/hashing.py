from passlib.context import CryptContext
import random
from task.routers.send_email import send_email
import string
from fastapi import HTTPException
from task.models import User
from sqlalchemy.orm import Session
"""
    For the password hashing we used the Hash,
    and for the verify the password we use verify.
"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def generate_random_password(length=10) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))
