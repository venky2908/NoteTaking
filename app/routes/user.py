from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import UserCreate, UserLogin, Token
from app.auth import get_password_hash, create_access_token, verify_password
from app.database import db

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    user_data = db['users'].find_one({"email": user.email})
    if user_data:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db['users'].insert_one({"email": user.email, "password": hashed_password})
    return {"msg": "User registered successfully"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    user_data = db['users'].find_one({"email": user.email})
    if not user_data or not verify_password(user.password, user_data['password']):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
