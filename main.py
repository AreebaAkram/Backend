from datetime import datetime
from fastapi import FastAPI, HTTPException
from typing import Any

# app an instance of fastapi
app = FastAPI(root_path="/api/v1") 

data : Any = [
    {"task_id" : 1,
     "task_name" : "Morning walk",
     "due_date" : datetime.now(),
     "created_at" : datetime.now()}
]

@app.get("/")
async def root():
    return {"message" : "hello world!"} 

@app.get("/tasks")
async def read_tasks():
    return {"tasks" : data}

@app.get("/tasks/{id}")
async def read_task(id : int):
    for task in data:
        if task.get("task_id") == id:
            return{"task" : task}
    raise HTTPException(status_code=404)