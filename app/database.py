from pymongo import MongoClient

class Settings:
    mongodb_url = "mongodb://localhost:27017"
    secret_key = "your_secret_key_here"
    algorithm = "HS256"
    access_token_expire_minutes = 30

settings = Settings()

client = MongoClient(settings.mongodb_url)
db = client['notebook-app']
users_collection = db['users']
notes_collection = db['notes']

