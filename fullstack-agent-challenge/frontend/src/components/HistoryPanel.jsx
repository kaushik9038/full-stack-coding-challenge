function formatTimestamp(timestamp) {
  return new Date(timestamp).toLocaleString();
}

export default function HistoryPanel({ tasks, selectedId, onSelect }) {
  return (
    <section className="panel history-panel">
      <h2>History</h2>
      {tasks.length ? (
        <ul className="history-list">
          {tasks.map((task) => (
            <li key={task.id}>
              <button
                type="button"
                className={task.id === selectedId ? "history-item active" : "history-item"}
                onClick={() => onSelect(task.id)}
              >
                <span className="history-task">{task.task}</span>
                <span className="history-meta">
                  {task.selected_tool} • {formatTimestamp(task.timestamp)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">No tasks yet.</p>
      )}
    </section>
  );
}
