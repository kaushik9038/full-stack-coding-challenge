# Fullstack Agent Challenge

This is a small local full-stack app built with a FastAPI backend and a React frontend.

The user enters a task, the backend validates it, analyzes intent, routes it to the appropriate tool when it is a supported single-intent request, stores the result, and shows the full trace in the UI.


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

- `POST /tasks` takes the task text, sends it through the controller, stores either the successful result or the rejected request trace, and returns the saved record when the task is accepted.
- `GET /tasks` returns task history.
- `GET /tasks/{id}` returns one task with the full execution trace.

The routing is rule-based and lightweight.

- Tools are registered through a small registry.
- Each tool carries its own scoring logic, so the controller can ask every tool for intent evidence without embedding tool-specific matching rules in one place.
- The controller flow is: validate task -> analyze intent -> resolve route -> execute or reject.
- Tool scores are used as routing evidence, not as the routing policy by themselves.
- If the request contains multiple supported intents, the controller rejects it and asks the user to split it into separate requests.
- If no tool reaches the confidence threshold, the controller rejects the task and asks the user to clarify it.

Right now there are 3 tools:

- `weather_mock`
- `calculator`
- `text_processor`

## Controller Flow

The backend controller now works in explicit phases:

1. Validate the incoming task text.
2. Analyze candidate intents from all registered tools.
3. Resolve the route as one of:
   - single supported intent
   - compound intent rejection
   - unresolved intent rejection
4. Execute the selected tool when a supported single intent is found.
5. Persist the final outcome and execution trace.

This keeps intent analysis separate from execution and makes failed or rejected requests visible in the UI history.

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
- Execution steps are stored as JSON text, mostly to keep the schema simple
- CORS is enabled for the local Vite frontend
- Adding a new tool means defining its handler and scoring logic, then registering it in the tool registry
- Rejected tasks are also persisted, so the history view includes failed validation, unresolved intent, and compound intent requests
- The UI is simple by design and includes task entry, history, final output, and full execution trace

## Current Limitations

- Weather is mock data with static predefined city lists
- The system supports only one tool per request
- Compound requests are rejected, multiple tool runs not supported
- Routing is rule-based and depends on keyword and pattern matching, not an LLM planner

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
Rejected: This request includes multiple intents. Please split the request into separate tasks and resubmit each one.

Input: hello there
Rejected: Intent cannot be validated with the current level of confidence. Please clarify the task.

Input: calculate 5 / 0
Rejected after tool selection: Division by zero is not supported.
```

## Trace Behavior

Each saved task includes an execution trace in the UI.

- Successful tasks show validation, intent analysis, routing, execution, and completion steps
- Rejected tasks show validation, intent analysis or routing details, and a final `failed` step
- Failed and rejected requests are stored in history so the reasoning path remains inspectable
