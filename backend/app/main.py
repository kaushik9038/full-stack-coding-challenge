"""Small FastAPI backend for the beginner task handler app.

This file keeps most of the API code in one place on purpose. It is not the
"cleanest enterprise architecture", but it is friendly when you are learning.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.tools.calculator import calculate_answer, looks_like_math
from app.tools.text_processor import handle_text_task, looks_like_text_task
from app.tools.weather_mock import get_weather_answer, looks_like_weather


DB_FILE = Path(__file__).resolve().parents[1] / "tasks.db"

app = FastAPI(title="Beginner Task Handler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskIn(BaseModel):
    task: str = Field(..., min_length=1, max_length=500)


class TaskOut(BaseModel):
    id: int
    task: str
    selected_tool: str
    final_output: str
    steps: list[dict]
    created_at: str


def connect_to_db():
    return sqlite3.connect(DB_FILE)


def setup_database():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            selected_tool TEXT NOT NULL,
            final_output TEXT NOT NULL,
            steps_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


def save_task(task_text: str, tool_name: str, final_output: str, steps: list[dict]) -> TaskOut:
    created_at = datetime.now(timezone.utc).isoformat()
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (task, selected_tool, final_output, steps_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_text, tool_name, final_output, json.dumps(steps), created_at),
    )
    connection.commit()
    new_id = cursor.lastrowid
    connection.close()

    return TaskOut(
        id=new_id,
        task=task_text,
        selected_tool=tool_name,
        final_output=final_output,
        steps=steps,
        created_at=created_at,
    )


def row_to_task(row) -> TaskOut:
    return TaskOut(
        id=row[0],
        task=row[1],
        selected_tool=row[2],
        final_output=row[3],
        steps=json.loads(row[4]),
        created_at=row[5],
    )


def pick_tool(task_text: str):
    """Pick one tool.

    The app is intentionally simple. Each tool gets a yes/no check. If more than
    one tool matches, we ask the user to split the request.
    """
    lower_task = task_text.lower()
    matches = []

    if looks_like_weather(lower_task):
        matches.append("weather")

    if looks_like_math(lower_task):
        matches.append("calculator")

    if looks_like_text_task(lower_task):
        matches.append("text_processor")

    if len(matches) > 1:
        raise ValueError("This looks like more than one task. Please enter one task at a time.")

    if len(matches) == 0:
        raise ValueError("I could not understand which tool to use. Try weather, calculate, uppercase, lowercase, or word count.")

    return matches[0]


def run_task(task_text: str):
    steps = []
    steps.append({"stage": "received", "message": "The backend received the task."})

    task_text = task_text.strip()
    if not task_text:
        raise ValueError("Task cannot be empty.")

    steps.append({"stage": "validated", "message": "The task is not empty."})

    tool_name = pick_tool(task_text)
    steps.append({"stage": "tool_selected", "message": f"Selected tool: {tool_name}"})

    if tool_name == "weather":
        final_output = get_weather_answer(task_text)
    elif tool_name == "calculator":
        final_output = calculate_answer(task_text)
    else:
        final_output = handle_text_task(task_text)

    steps.append({"stage": "finished", "message": "The tool finished running."})
    return tool_name, final_output, steps


@app.on_event("startup")
def startup_event():
    setup_database()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskOut)
def create_task(payload: TaskIn):
    try:
        tool_name, final_output, steps = run_task(payload.task)
        return save_task(payload.task.strip(), tool_name, final_output, steps)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, task, selected_tool, final_output, steps_json, created_at
        FROM tasks
        ORDER BY id DESC
        """
    )
    rows = cursor.fetchall()
    connection.close()
    return [row_to_task(row) for row in rows]
