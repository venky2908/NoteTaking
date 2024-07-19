# NoteTaking
Note-Taking Application
A simple note-taking application built with FastAPI, React, and MongoDB.

Features
User Registration and Login
JWT-based Authentication
CRUD Operations for Notes
Setup Instructions
Clone the repository:
git clone <repository-url>
cd <repository-folder>\backend

Create a virtual environment and activate it:

python -m venv venv

.\venv\Scripts\activate

Install the dependencies:
pip install -r requirements.txt

Run the FastAPI server:

uvicorn main:app --reload

Navigate to the frontend directory:
cd <repository-folder>\frontend

Install the dependencies:

npm install

Set up environment variables: Create a .env file in the frontend directory with the following content:
VITE_API_URL=http://127.0.0.1:8000

Run the React development server:
npm run dev

Start the backend server:
cd <repository-folder>\backend
.\venv\Scripts\activate

uvicorn main:app --reload

Start the frontend server:
cd <repository-folder>\frontend
npm run dev

Access the application by opening your browser and navigating to http://localhost:5173.

