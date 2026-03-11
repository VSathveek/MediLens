import './ReasoningDisplay.css'

function ReasoningDisplay({ reasoning }) {
  if (!reasoning) {
    return (
      <div className="reasoning-display">
        <h3>🤖 AI Medical Reasoning</h3>
        <div className="reasoning-content">
          <p className="no-reasoning">No reasoning available</p>
        </div>
      </div>
    )
  }

  const cleaned = reasoning
    .replace(/\*\*/g, '')
    .replace(/\n\s*\n/g, '\n')
    .trim()

  const lines = cleaned.split('\n').filter((line) => line.trim().length > 0)

  return (
    <div className="reasoning-display card">
      <h3>🤖 AI Medical Thought Process</h3>
      <div className="reasoning-content">
        {lines.map((line, index) => (
          <p key={index} className="reasoning-line">
            {line.replace(/^\s*[-*•]/, '').trim()}
          </p>
        ))}
      </div>
    </div>
  )
}

export default ReasoningDisplay