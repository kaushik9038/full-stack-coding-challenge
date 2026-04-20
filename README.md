# Beginner Task Handler

This is a beginner-friendly version of the full-stack task handler project.

It has:

- A Python FastAPI backend
- A tiny SQLite database
- A React frontend made with Vite
- Three simple tools:
  - weather mock
  - calculator
  - text processor

The goal is not to make the fanciest version. The goal is to make a version that
someone can read without already being comfortable with React or backend design.

## Folder Structure

```text
beginner-task-handler/
  backend/
    requirements.txt
    app/
      main.py
      tools/
        calculator.py
        text_processor.py
        weather_mock.py
  frontend/
    package.json
    index.html
    src/
      main.jsx
      styles.css
```

## What The App Does

You type a task into the frontend.

Example tasks:

```text
calculate 5 * 8
what is the weather in Edmonton
uppercase hello world
lowercase HELLO WORLD
word count this sentence has five words
```

The backend:

1. Receives the task.
2. Checks which tool should handle it.
3. Runs the tool.
4. Saves the result in SQLite.
5. Sends the result back to the frontend.

## Run The Backend

From this folder:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Run The Frontend

Open a second terminal.

From this folder:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:5173
```

## Important Beginner Notes

The frontend API URL is hardcoded here:

```text
frontend/src/main.jsx
```

The backend database file is created here after you run the backend:

```text
backend/tasks.db
```

The backend keeps the code simple on purpose. In a production app, you would
usually split database code, API routes, settings, and business logic into
separate files.

## What Is Intentionally Not Fancy

This version does not use:

- SQLAlchemy
- Alembic migrations
- Authentication
- Environment variables
- Many React components
- A production deployment setup

Those are useful later. This version is for learning the moving parts first.
