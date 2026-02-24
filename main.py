from contextlib import asynccontextmanager
from datetime import datetime, timezone
from random import randint
from fastapi import Depends, FastAPI, HTTPException, Response
from typing import Annotated, Any

from sqlmodel import Field, SQLModel, Session, create_engine, select

class tasks(SQLModel, table = True):
    task_id : int | None = Field(default=None, primary_key = True)
    name : str = Field(index = True)
    due_date : datetime | None = Field(default = None, index = True)
    created_at : datetime = Field(default_factory=lambda:datetime.now(timezone.utc), nullable=True, index= True)

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
                tasks(name = "walk", due_date=datetime.now()),
                tasks(name = "sleep", due_date= datetime.now())
            ])
            session.commit()
    yield
    
# app an instance of fastapi
app = FastAPI(root_path="/api/v1", lifespan=lifespan) 

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
async def get_tasks(session : SessionDep):
    data = session.exec(select(tasks)).all()
    return {"tasks" : data}

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