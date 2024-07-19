# notes_crud.py

from bson import ObjectId
from database import notes_collection

def create_note(note_data):
    result = notes_collection.insert_one(note_data)
    return str(result.inserted_id)

def get_all_notes():
    notes = list(notes_collection.find())
    return notes

def get_note_by_id(note_id):
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    return note

def update_note(note_id, updated_data):
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": updated_data}
    )
    return result.modified_count

def delete_note(note_id):
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    return result.deleted_count
