import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from time import time , sleep
from fastapi.middleware.cors import CORSMiddleware

class BaseTodo(BaseModel):
    task: str

class TodoItem(BaseTodo):
    id: Optional[int] = None
    is_done: bool = False

class ReturnTodo(BaseTodo):
    pass

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

todos = []


@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    print(f"Time taken to process request: {process_time}")
    return response


@app.get("/")
def read_root():
    return {"message": "Hello World"}


async def send_email(background_tasks: BackgroundTasks):
    print("Sending email...")
    sleep(10)
    print("Email sent.")

@app.post("/todos/" , response_model=ReturnTodo)
async def create_todos(todo: TodoItem , background_task: BackgroundTasks):
    todo.id = len(todos) + 1
    todos.append(todo)
    background_task.add_task(send_email)
    return todo


@app.get("/todos/")
async def get_todos(done : Optional[bool] = None):
    if done is None:
        return todos
    else:
        return [todo for todo in todos if todo.is_done == done]

@app.get("/todos/{todo_id}")
async def get_todo_by_id(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@app.put("/todos/{todo_id}")
async def update_todo_by_id(todo_id: int, new_todo: TodoItem):
    for todo in todos:
        if todo.id == todo_id:
            todo.task = new_todo.task
            todo.is_done = new_todo.is_done
            return {"message": "Todo updated successfully.", "todo": todo}
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}")
async def delete_todo_by_id(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            todos.remove(todo)
            return {"message": "Todo deleted successfully."}
    raise HTTPException(status_code=404, detail="Todo not found")



if __name__ == "__main__":
    uvicorn.run("__main__:app", host="127.0.0.1", port=8000 , reload=True)
