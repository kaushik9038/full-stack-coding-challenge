import { useEffect, useState } from "react";
import { createTask, fetchTask, fetchTasks } from "./api";
import HistoryPanel from "./components/HistoryPanel";
import ResultPanel from "./components/ResultPanel";
import TaskForm from "./components/TaskForm";

function formatTaskError(message) {
  if (message.includes("multiple operations") || message.includes("multiple intents")) {
    return {
      title: "Compound task not supported",
      message: "This request combines multiple operations. Split it into separate text, weather, or calculation tasks.",
    };
  }

  if (message.includes("cannot be validated with the current level of confidence")) {
    return {
      title: "Intent not validated",
      message: "The controller could not determine one intent with enough confidence. Rephrase the task more explicitly.",
    };
  }

  return {
    title: "Request failed",
    message,
  };
}

export default function App() {
  const [task, setTask] = useState("");
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Good enough for this app. No need to get fancy with a data layer yet.
    loadTasks();
  }, []);

  async function loadTasks({ selectLatest = false } = {}) {
    try {
      const history = await fetchTasks();
      setTasks(history);
      // First load looks empty otherwise, which feels broken even when it isn't.
      if (history.length && (selectLatest || !selectedTask)) {
        setSelectedTask(history[0]);
      }
    } catch (requestError) {
      setError(formatTaskError(requestError.message));
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!task.trim()) {
      setError({ title: "Missing task", message: "Please enter a task." });
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const createdTask = await createTask(task.trim());
      setSelectedTask(createdTask);
      setTask("");
      await loadTasks({ selectLatest: true });
    } catch (requestError) {
      await loadTasks({ selectLatest: true });
      setError(formatTaskError(requestError.message));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSelect(taskId) {
    try {
      setError(null);
      const loadedTask = await fetchTask(taskId);
      setSelectedTask(loadedTask);
    } catch (requestError) {
      setError(formatTaskError(requestError.message));
    }
  }

  return (
    <main className="app-shell">
      <section className="left-column">
        <header className="page-header">
          <h1>Agent Task Runner</h1>
          <p>A small FastAPI + React demo with simple tool routing and trace history.</p>
        </header>
        <TaskForm
          task={task}
          onTaskChange={setTask}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          error={error}
        />
        <ResultPanel result={selectedTask} />
      </section>
      <aside className="right-column">
        <HistoryPanel tasks={tasks} selectedId={selectedTask?.id} onSelect={handleSelect} />
      </aside>
    </main>
  );
}
