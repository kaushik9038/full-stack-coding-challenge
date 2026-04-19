# Fullstack Agent Challenge

This is a small local full-stack app built with a FastAPI backend and a React frontend.

The user will type in a task, the backend figure out the intent of the task and route it to the appropriate tool to handle it, run that tool, save the result, and show the trace in the UI.


## Project Structure

```text
fullstack-agent-challenge/
  README.md
  backend/
    app/
      agent/
        audit_logger.py
        controller.py
        registry.py
        tool_definitions.py
      api/
        routes/
          task_routes.py
      db/
        models.py
        schemas.py
        session.py
      services/
        task_service.py
      tools/
        calculator.py
        text_processor.py
        weather_mock.py
      main.py
    requirements.txt
    tasks.db
  frontend/
    src/
      components/
        HistoryPanel.jsx
        ResultPanel.jsx
        TaskForm.jsx
      App.jsx
      api.js
      main.jsx
      styles.css
    index.html
    package.json
    vite.config.js
```

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend should come up on `http://127.0.0.1:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173`.

## How It Works

- `POST /tasks` takes the task text, sends it through the controller, runs one tool, stores the result, and returns the saved record.
- `GET /tasks` returns task history.
- `GET /tasks/{id}` returns one task with the full execution trace.

The routing is rule-based and lightweight.

- Tools are registered through a small registry.
- Each tool carries its own scoring logic, so the controller does not need to know all the details.
- The scoring logic of each tool is a numeric value based on specific keywords it can find on the task request
- The controller compares scores and picks the best one.
- If a request has more than one intent in it, the controller compares the scoring from the tools and the highest scorer is awarded the task.

Right now there are 3 tools:

- `weather_mock`
- `calculator`
- `text_processor`

## Example Tasks

- `uppercase hello world`
- `lowercase THIS SHOULD BE QUIET`
- `word count this sentence has five words`
- `calculate 5 * 8`
- `what is the weather in Edmonton`
- `calculate 2 + 2 and weather in Edmonton`
- `weather in Edmonton and calculate 2 + 2`

## Notes

- SQLite lives locally in `backend/tasks.db`
- Execution steps are stored as JSON text, mostly to keep the schema boring
- CORS is enabled for the local Vite frontend
- Adding a new tool is adding the tool handler and adding it to tool registry, the controller automatically loops through all registered tools
- The UI is simple by design covering all necessary sections for task entry, history, task tracker.

## Tested Inputs and Outputs

The following inputs were run against the current backend controller and produced these outputs:

```text
Input: uppercase hello world
Selected tool: text_processor
Output: HELLO WORLD

Input: word count this sentence has five words
Selected tool: text_processor
Output: Word count: 5

Input: calculate 5 * 8
Selected tool: calculator
Output: 40

Input: what is the weather in Edmonton
Selected tool: weather_mock
Output: Edmonton: 8°C, Windy

Input: calculate 2 + 2 and weather in Edmonton
Selected tool: calculator
Output: 4
```
