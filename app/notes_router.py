from fastapi import APIRouter, HTTPException, Path, Body, Depends
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId
from database import db
from schemas import get_current_user

router = APIRouter()

# MongoDB collection
notes_collection = db["notes"]  # Adjust collection name as needed

class NoteSchema(BaseModel):
    title: str
    content: str

class NoteUpdateSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

def create_note(note_data: dict) -> str:
    result = notes_collection.insert_one(note_data)
    return str(result.inserted_id)

def get_all_notes(user: dict) -> List[dict]:
    notes = list(notes_collection.find({"user_id": user["_id"]}))
    for note in notes:
        note["_id"] = str(note["_id"])
    return notes

def get_note_by_id(note_id: str, user: dict) -> Optional[dict]:
    note = notes_collection.find_one({"_id": ObjectId(note_id), "user_id": user["_id"]})
    if note:
        note["_id"] = str(note["_id"])
    return note

def update_note(note_id: str, updated_data: dict, user: dict) -> int:
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id), "user_id": user["_id"]},
        {"$set": updated_data}
    )
    return result.modified_count

def delete_note(note_id: str, user: dict) -> int:
    result = notes_collection.delete_one({"_id": ObjectId(note_id), "user_id": user["_id"]})
    return result.deleted_count

@router.post("/notes/", response_model=str)
def create_note_api(note: NoteSchema = Body(...), current_user: dict = Depends(get_current_user)):
    note_data = note.dict()
    note_data["user_id"] = current_user["_id"]
    note_id = create_note(note_data)
    return note_id

@router.get("/notes/", response_model=List[NoteSchema])
def read_all_notes(current_user: dict = Depends(get_current_user)):
    return get_all_notes(current_user)

@router.get("/notes/{note_id}", response_model=NoteSchema)
def read_note(note_id: str = Path(..., title="The ID of the note to retrieve"), current_user: dict = Depends(get_current_user)):
    note = get_note_by_id(note_id, current_user)
    if note:
        return note
    else:
        raise HTTPException(status_code=404, detail="Note not found")

@router.put("/notes/{note_id}", response_model=int)
def update_note_api(
    note_id: str = Path(..., title="The ID of the note to update"),
    updated_note: NoteSchema = Body(...),
    current_user: dict = Depends(get_current_user)
):
    updated_data = updated_note.dict(exclude_unset=True)
    updated_count = update_note(note_id, updated_data, current_user)
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_count

@router.patch("/notes/{note_id}", response_model=int)
def partial_update_note_api(
    note_id: str = Path(..., title="The ID of the note to update"),
    updated_note: NoteUpdateSchema = Body(...),
    current_user: dict = Depends(get_current_user)
):
    updated_data = updated_note.dict(exclude_unset=True)
    updated_count = update_note(note_id, updated_data, current_user)
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_count

@router.delete("/notes/{note_id}", response_model=int)
def delete_note_api(note_id: str = Path(..., title="The ID of the note to delete"), current_user: dict = Depends(get_current_user)):
    deleted_count = delete_note(note_id, current_user)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return deleted_count
