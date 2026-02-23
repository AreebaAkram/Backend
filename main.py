from datetime import datetime
from random import randint
from fastapi import FastAPI, HTTPException, Request, Response
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

@app.post("/tasks")
async def create_task(body : dict[str, Any]):

    new : Any =  {"task_id" : randint(100, 200),
     "task_name" : body.get("name"),
     "due_date" : body.get("due_date"),
     "created_at" : datetime.now()
     }
    data.append(new)
    return{"tasks" : new}

@app.put("/tasks/{id}")
async def update_task(id : int, body : dict[str, Any]):
    for index, task in enumerate(data):
        if task.get("task_id") == id:
            updated : Any =  {
                "task_id" : id,
                "task_name" : body.get("name"),
                "due_date" : body.get("due_date"),
                "created_at" : task.get("created_at")
            }
            data[index] = updated
            return{"task" : updated}
    raise HTTPException(status_code=404)

@app.delete("/tasks/{id}")
async def delete_task(id: int):
    for index, task in enumerate(data):
        if task.get("task_id") == id:
            data.pop(index)
            return Response(status_code=204)
    raise HTTPException(status_code=404)