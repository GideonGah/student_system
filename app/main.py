from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import json
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# File paths
USERS_FILE = "users.json"
LECTURERS_FILE = "lecturers.json"
EVALUATIONS_FILE = "evaluations.json"

# Ensure JSON files exist
def ensure_files_exist():
    for file in [USERS_FILE, LECTURERS_FILE, EVALUATIONS_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump([], f)

ensure_files_exist()

# Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr

class LecturerCreate(BaseModel):
    name: str
    department: str

class EvaluationCreate(BaseModel):
    user_index: str
    lecturer_id: str
    rating: int  # Assume rating is between 1 and 5
    comments: str | None = None

# Utility functions
def read_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def write_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def generate_user_index():
    users = read_json(USERS_FILE)
    return f"{len(users) + 1:04d}"

def generate_lecturer_id():
    lecturers = read_json(LECTURERS_FILE)
    return f"L{len(lecturers) + 1:04d}"

# Endpoints

@app.post("/register", response_model=dict)
def register_user(user: UserCreate):
    users = read_json(USERS_FILE)
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="User already exists")

    user_index = generate_user_index()
    users.append({"index": user_index, "name": user.name, "email": user.email})
    write_json(USERS_FILE, users)
    return {"index": user_index, "message": "User registered successfully"}

@app.post("/lecturers", response_model=dict)
def add_lecturer(lecturer: LecturerCreate):
    lecturers = read_json(LECTURERS_FILE)
    lecturer_id = generate_lecturer_id()
    lecturers.append({"id": lecturer_id, "name": lecturer.name, "department": lecturer.department})
    write_json(LECTURERS_FILE, lecturers)
    return {"lecturer_id": lecturer_id, "message": "Lecturer added successfully"}

@app.get("/lecturers", response_model=List[dict])
def list_lecturers():
    lecturers = read_json(LECTURERS_FILE)
    return lecturers

@app.post("/evaluate", response_model=dict)
def evaluate_lecturer(evaluation: EvaluationCreate):
    users = read_json(USERS_FILE)
    lecturers = read_json(LECTURERS_FILE)
    evaluations = read_json(EVALUATIONS_FILE)

    if not any(u["index"] == evaluation.user_index for u in users):
        raise HTTPException(status_code=404, detail="User not found")

    if not any(l["id"] == evaluation.lecturer_id for l in lecturers):
        raise HTTPException(status_code=404, detail="Lecturer not found")

    if evaluation.rating < 1 or evaluation.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    evaluations.append({
        "user_index": evaluation.user_index,
        "lecturer_id": evaluation.lecturer_id,
        "rating": evaluation.rating,
        "comments": evaluation.comments
    })
    write_json(EVALUATIONS_FILE, evaluations)
    return {"message": "Evaluation submitted successfully"}

@app.get("/evaluations", response_model=List[dict])
def get_evaluations():
    evaluations = read_json(EVALUATIONS_FILE)
    return evaluations

@app.get("/")
def read_root():
    return {"message": "Hello, guys!"}



if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Use 8000 if $PORT is not set
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)


# Run the application
# Use `uvicorn madel:app --reload` to run this FastAPI application.




