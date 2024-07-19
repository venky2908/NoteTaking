import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from notes_router import router as notes_router  # Adjust the import as per your project structure

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",  # Replace with your frontend URL
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notes_router, prefix="/api", tags=["notes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Notes API"}


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
