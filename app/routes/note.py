from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import NoteCreate, NoteUpdate, NoteResponse
from app.auth import get_current_user
from app.database import db
from bson import ObjectId
from typing import List

router = APIRouter()

@router.post("/", response_model=NoteResponse)
async def create_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    note_data = note.dict()
    note_data['user_id'] = current_user.username
    result = db['notes'].insert_one(note_data)
    note_data['id'] = str(result.inserted_id)
    return note_data

@router.get("/", response_model=List[NoteResponse])
async def get_notes(current_user: dict = Depends(get_current_user)):
    notes = list(db['notes'].find({"user_id": current_user.username}))
    for note in notes:
        note['id'] = str(note['_id'])
    return notes

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str, current_user: dict = Depends(get_current_user)):
    note = db['notes'].find_one({"_id": ObjectId(note_id), "user_id": current_user.username})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note['id'] = str(note['_id'])
    return note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note: NoteUpdate, current_user: dict = Depends(get_current_user)):
    result = db['notes'].update_one(
        {"_id": ObjectId(note_id), "user_id": current_user.username},
        {"$set": note.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    updated_note = db['notes'].find_one({"_id": ObjectId(note_id)})
    updated_note['id'] = str(updated_note['_id'])
    return updated_note

@router.delete("/{note_id}", response_model=dict)
async def delete_note(note_id: str, current_user: dict = Depends(get_current_user)):
    result = db['notes'].delete_one({"_id": ObjectId(note_id), "user_id": current_user.username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"msg": "Note deleted successfully"}
