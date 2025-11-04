# schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    phone: str | None = None
    email: EmailStr
    password: str
