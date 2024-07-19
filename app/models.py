from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId  # Add this import for ObjectId

class User(BaseModel):
    username: str
    email: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class NoteEntry(BaseModel):
    user_id: str
    title: str
    content: str

class NoteEntryResponse(NoteEntry):
    id: str = Field(default_factory=lambda: str(ObjectId()))
