from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from cc_simple_server.models import TaskCreate
from cc_simple_server.models import TaskRead
from cc_simple_server.database import init_db
from cc_simple_server.database import get_db_connection

# init
init_db()

app = FastAPI()

############################################
# Edit the code below this line
############################################


@app.get("/")
async def read_root():
    """
    This is already working!!!! Welcome to the Cloud Computing!
    """
    return {"message": "Welcome to the Cloud Computing!"}


# POST ROUTE data is sent in the body of the request
@app.post("/tasks/", response_model=TaskRead)
async def create_task(task_data: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert a new task record
    cursor.execute(
        """
        INSERT INTO tasks (title, description, completed)
        VALUES (?, ?, ?)
        """,
        (task_data.title, task_data.description, task_data.completed)
    )
    conn.commit()
    new_id = cursor.lastrowid  # Get the auto-increment primary key ID

    # Check again and return the complete record
    cursor.execute(
        "SELECT id, title, description, completed FROM tasks WHERE id = ?",
        (new_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        # Theoretically, it won't happen, but just in case
        raise HTTPException(status_code=404, detail="Created task not found")


    return TaskRead(**dict(row))


# GET ROUTE to get all tasks
@app.get("/tasks/", response_model=list[TaskRead])
async def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query all tasks
    cursor.execute("SELECT id, title, description, completed FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    # Convert each line into a TaskRead instance
    tasks = [TaskRead(**dict(row)) for row in rows]
    return tasks



# UPDATE ROUTE data is sent in the body of the request and the task_id is in the URL
@app.put("/tasks/{task_id}/", response_model=TaskRead)
async def update_task(task_id: int, task_data: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # First check if this task exists
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    exists = cursor.fetchone()
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    # Performing Updates
    cursor.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, completed = ?
        WHERE id = ?
        """,
        (task_data.title, task_data.description, task_data.completed, task_id)
    )
    conn.commit()

    # Check the updated records again
    cursor.execute(
        "SELECT id, title, description, completed FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Task not found after update")

    return TaskRead(**dict(row))

# DELETE ROUTE task_id is in the URL
@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if this task exists
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    exists = cursor.fetchone()
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    # Execute Delete
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


    # {"message": "Task {task_id} deleted successfully"}
    return {"message": f"Task {task_id} deleted successfully"}
