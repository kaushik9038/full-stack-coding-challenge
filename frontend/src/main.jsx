import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [taskText, setTaskText] = useState("");
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    try {
      const response = await fetch(`${API_URL}/tasks`);
      const data = await response.json();
      setTasks(data);

      if (data.length > 0 && selectedTask === null) {
        setSelectedTask(data[0]);
      }
    } catch (error) {
      setErrorMessage("Could not load task history. Is the backend running?");
    }
  }

  async function submitTask(event) {
    event.preventDefault();
    setErrorMessage("");

    if (taskText.trim() === "") {
      setErrorMessage("Please type a task first.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/tasks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ task: taskText }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setTaskText("");
      setSelectedTask(data);
      await loadTasks();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="main-area">
        <h1>Beginner Task Handler</h1>
        <p className="intro">Try weather, calculator, uppercase, lowercase, or word count tasks.</p>

        <form className="task-form" onSubmit={submitTask}>
          <input
            value={taskText}
            onChange={(event) => setTaskText(event.target.value)}
            placeholder="Example: calculate 5 * 8"
          />
          <button disabled={isLoading}>{isLoading ? "Running..." : "Run Task"}</button>
        </form>

        {errorMessage && <div className="error-box">{errorMessage}</div>}

        <section className="result-box">
          <h2>Result</h2>

          {!selectedTask && <p>No task selected yet.</p>}

          {selectedTask && (
            <>
              <p>
                <strong>Task:</strong> {selectedTask.task}
              </p>
              <p>
                <strong>Tool:</strong> {selectedTask.selected_tool}
              </p>
              <p>
                <strong>Output:</strong> {selectedTask.final_output}
              </p>

              <h3>Steps</h3>
              <ol>
                {selectedTask.steps.map((step, index) => (
                  <li key={`${step.stage}-${index}`}>
                    <strong>{step.stage}:</strong> {step.message}
                  </li>
                ))}
              </ol>
            </>
          )}
        </section>
      </section>

      <aside className="history">
        <h2>History</h2>

        {tasks.length === 0 && <p>No saved tasks yet.</p>}

        {tasks.map((task) => (
          <button
            className="history-item"
            key={task.id}
            onClick={() => setSelectedTask(task)}
          >
            <span>{task.task}</span>
            <small>{task.selected_tool}</small>
          </button>
        ))}
      </aside>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
