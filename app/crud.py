# crud_operations.py

from database import db

def create_document(collection_name, document):
    collection = db[collection_name]
    result = collection.insert_one(document)
    return str(result.inserted_id)

def read_documents(collection_name, query=None):
    collection = db[collection_name]
    documents = list(collection.find(query)) if query else list(collection.find())
    return documents

def update_document(collection_name, query, update):
    collection = db[collection_name]
    result = collection.update_one(query, {"$set": update})
    return result.modified_count

def delete_document(collection_name, query):
    collection = db[collection_name]
    result = collection.delete_one(query)
    return result.deleted_count
