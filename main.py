from datetime import datetime, timedelta, timezone
from typing import Optional, List

import jwt
from jwt import PyJWTError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel, Field

# Configuration settings
class Settings:
    mongodb_url = "mongodb://localhost:27017"
    secret_key = "your_secret_key_here"
    algorithm = "HS256"
    access_token_expire_minutes = 30

settings = Settings()

# MongoDB setup
client = MongoClient(settings.mongodb_url)
db = client['notes-app']
users_collection = db['users']
notes_collection = db['notes']

# Models
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

class NoteEntry(BaseModel):
    user_id: str
    title: str
    description: str

class NoteEntryResponse(NoteEntry):
    id: str = Field(default_factory=lambda: str(ObjectId()))

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_user(email: str):
    user_dict = users_collection.find_one({"email": email})
    if user_dict:
        return UserInDB(**user_dict)

# FastAPI app
app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register")
async def register(user: RegisterRequest):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    user_dict = {"username": user.username, "email": user.email, "hashed_password": hashed_password}
    users_collection.insert_one(user_dict)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login(user_cred: LoginRequest):
    user = get_user(user_cred.email)
    if not user or not verify_password(user_cred.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        response = JSONResponse(content={"message": "Logout successful"})
        response.delete_cookie(key="Authorization")
        return response
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/notes/", response_class=JSONResponse, response_model=NoteEntryResponse)
async def create_note_entry(
    entry: NoteEntry,
    current_user: UserInDB = Depends(get_current_user)
):
    entry_dict = entry.dict()
    entry_dict['user_id'] = current_user.email
    result = notes_collection.insert_one(entry_dict)
    entry_id = str(result.inserted_id)

    response_data = {
        "id": entry_id,
        "title": entry.title,
        "description": entry.description,
        "user_id": current_user.email  # Ensure user_id is set correctly
    }
    return response_data

@app.get("/notes/", response_class=JSONResponse, response_model=List[NoteEntryResponse])
async def read_note_entries(current_user: UserInDB = Depends(get_current_user)):
    entries = list(notes_collection.find({"user_id": current_user.email}))
    
    response_data = []
    for entry in entries:
        response_data.append(NoteEntryResponse(
            id=str(entry.get('_id')),
            title=entry.get('title'),
            description=entry.get('description'),
            user_id=entry.get('user_id')
        ))
    
    return response_data

@app.get("/notes/{entry_id}", response_class=JSONResponse, response_model=NoteEntryResponse)
async def read_note_entry(
    entry_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    entry = notes_collection.find_one({"_id": ObjectId(entry_id), "user_id": current_user.email})
    if entry:
        response_data = {
            "id": str(entry.get('_id')),
            "title": entry.get('title'),
            "description": entry.get('description'),
            "user_id": entry.get('user_id')
        }
        return response_data
    raise HTTPException(status_code=404, detail="Note entry not found")

@app.put("/notes/{entry_id}", response_class=JSONResponse, response_model=NoteEntryResponse)
async def update_note_entry(
    entry_id: str,
    entry: NoteEntry,
    current_user: UserInDB = Depends(get_current_user)
):
    entry_dict = entry.dict()
    entry_dict.pop('user_id')
    existing_entry = notes_collection.find_one({"_id": ObjectId(entry_id), "user_id": current_user.email})
    if existing_entry:
        result = notes_collection.update_one({"_id": ObjectId(entry_id)}, {"$set": entry_dict})
        if result.modified_count == 1:
            response_data = {
                "id": entry_id,
                "title": entry.title,
                "description": entry.description,
                "user_id": entry.user_id
            }
            return response_data
    raise HTTPException(status_code=404, detail="Note entry not found")

@app.delete("/notes/{entry_id}", response_class=JSONResponse)
async def delete_note_entry(
    entry_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    result = notes_collection.delete_one({"_id": ObjectId(entry_id), "user_id": current_user.email})
    if result.deleted_count == 1:
        return {"message": "Note entry deleted successfully"}
    raise HTTPException(status_code=404, detail="Note entry not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)