function formatTimestamp(timestamp) {
  return new Date(timestamp).toLocaleString();
}

function formatValue(value) {
  if (Array.isArray(value)) {
    // Not pretty, but readable enough for a trace panel.
    return value.map((item) => (typeof item === "object" ? JSON.stringify(item) : String(item))).join(", ");
  }

  if (value && typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

export default function ResultPanel({ result }) {
  return (
    <section className="panel">
      <h2>Result</h2>
      {result ? (
        <div className="result-stack">
          <div>
            <span className="label">Task</span>
            <p>{result.task}</p>
          </div>
          <div>
            <span className="label">Selected Tool</span>
            <p>{result.selected_tool}</p>
          </div>
          <div>
            <span className="label">Output</span>
            <p>{result.final_output}</p>
          </div>
          <div>
            <span className="label">Timestamp</span>
            <p>{formatTimestamp(result.timestamp)}</p>
          </div>
          <div>
            <span className="label">Trace</span>
            <ul className="trace-list">
              {result.execution_steps.map((step, index) => (
                <li key={`${step.stage}-${index}`}>
                  <strong>{step.stage}</strong>
                  <span>{step.message}</span>
                  {Object.keys(step.details || {}).length ? (
                    <dl className="trace-details">
                      {Object.entries(step.details).map(([key, value]) => (
                        <div key={key}>
                          <dt>{key}</dt>
                          <dd>{formatValue(value)}</dd>
                        </div>
                      ))}
                    </dl>
                  ) : null}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <p className="muted">Submit a task to see the trace and output.</p>
      )}
    </section>
  );
}
