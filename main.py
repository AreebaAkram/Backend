from contextlib import asynccontextmanager
from datetime import datetime, timezone
from random import randint
from fastapi import Depends, FastAPI, HTTPException, Response
from typing import Annotated, Any, Generic, List, TypeVar

from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select

class tasks(SQLModel, table = True):
    task_id : int | None = Field(default=None, primary_key = True)
    name : str = Field(index = True)
    due_date : datetime | None = Field(default = None, index = True)
    created_at : datetime = Field(default_factory=lambda:datetime.now(timezone.utc), index= True)

class CreateTask(SQLModel):
    name : str
    due_date : datetime | None = None

sqlite_file_name = "file.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread" : False}
engine = create_engine(sqlite_url, connect_args= connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)] 

@asynccontextmanager
async def lifespan(app : FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(tasks)).first():
            session.add_all([
                tasks(name = "walk", due_date=datetime.now(timezone.utc)),
                tasks(name = "sleep", due_date= datetime.now(timezone.utc))
            ])
            session.commit()
    yield
    
# app an instance of fastapi
app = FastAPI(root_path="/api/v1", lifespan=lifespan) 

# data : Any = [
#     {"task_id" : 1,
#      "task_name" : "Morning walk",
#      "due_date" : datetime.now(),
#      "created_at" : datetime.now()}
# ]

# class tasks_Response(BaseModel):
#     task : List[tasks]

T = TypeVar("T")

class response(BaseModel, Generic[T]):
    data : T

@app.get("/")
async def root():
    return {"message" : "hello world!"} 

@app.get("/tasks", response_model=response[list[tasks]])
async def get_tasks(session : SessionDep):
    data = session.exec(select(tasks)).all()
    return {"data" : data}

@app.get("/tasks/{id}", response_model = response[tasks])
async def read_tasks(id : int, session : SessionDep):
    data = session.get(tasks, id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data" : data}
    
@app.post("/tasks", status_code=201, response_model = response[tasks])
async def create_task(task : CreateTask, session : SessionDep):
    db_tasks = tasks.model_validate(task)
    session.add(db_tasks)
    session.commit()
    session.refresh(db_tasks)
    return {"data" : db_tasks}

@app.put("/tasks/{id}", response_model = response[tasks])
async def update_task(id : int, task : CreateTask, session : SessionDep):
    data = session.get(tasks, id)
    if not data:
        raise HTTPException(status_code=404)
    data.name = task.name
    data.due_date = task.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data" : data}

@app.delete("/tasks/{id}", status_code = 204)
async def delete_task(id : int, session : SessionDep):
    data = session.get(tasks, id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()
    
# @app.get("/tasks")
# async def read_tasks():
#     return {"tasks" : data}

# @app.get("/tasks/{id}")
# async def read_task(id : int):
#     for task in data:
#         if task.get("task_id") == id:
#             return{"task" : task}
#     raise HTTPException(status_code=404)

# @app.post("/tasks")
# async def create_task(body : dict[str, Any]):

#     new : Any =  {"task_id" : randint(100, 200),
#      "task_name" : body.get("name"),
#      "due_date" : body.get("due_date"),
#      "created_at" : datetime.now()
#      }
#     data.append(new)
#     return{"tasks" : new}

# @app.put("/tasks/{id}")
# async def update_task(id : int, body : dict[str, Any]):
#     for index, task in enumerate(data):
#         if task.get("task_id") == id:
#             updated : Any =  {
#                 "task_id" : id,
#                 "task_name" : body.get("name"),
#                 "due_date" : body.get("due_date"),
#                 "created_at" : task.get("created_at")
#             }
#             data[index] = updated
#             return{"task" : updated}
#     raise HTTPException(status_code=404)

# @app.delete("/tasks/{id}")
# async def delete_task(id: int):
#     for index, task in enumerate(data):
#         if task.get("task_id") == id:
#             data.pop(index)
#             return Response(status_code=204)
#     raise HTTPException(status_code=404)