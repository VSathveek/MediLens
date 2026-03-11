import './ResultsDisplay.css'

export default function ResultsDisplay({ data }) {
  if (!data) return null

  const extractedMedicines = data.extraction?.medicines || []
  const answer = data.answer || data.reasoning || ''
  const references = data.references || data.rag_results || []

  return (
    <div className="results-display">
      <div className="result-section">
        <h3>📋 User Question</h3>
        <p className="input-text">{data.question || data.input || ''}</p>
        {data.input && data.input.length > 500 && (
          <p className="truncated-note">... (truncated)</p>
        )}
      </div>

      {answer && (
        <div className="result-section">
          <h3>🧠 AI Medical Answer</h3>
          <p className="answer-text">{answer}</p>
        </div>
      )}

      {references && references.length > 0 && (
        <div className="result-section">
          <h3>📚 References</h3>
          <ul className="reference-list">
            {references.map((ref, idx) => (
              <li key={idx}>{ref.text?.substring(0, 300) || JSON.stringify(ref)}</li>
            ))}
          </ul>
        </div>
      )}

      {extractedMedicines && extractedMedicines.length > 0 && (
        <div className="result-section">
          <h3>💊 Extracted Medicines</h3>
          <div className="medicines-list">
            {extractedMedicines.map((medicine, idx) => (
              <div key={idx} className="medicine-card">
                <div className="medicine-name">{medicine.name}</div>
                <div className="medicine-details">
                  <span className="detail">
                    <strong>Dosage:</strong> {medicine.dosage}
                  </span>
                  <span className="detail">
                    <strong>Frequency:</strong> {medicine.frequency}
                  </span>
                  <span className="detail">
                    <strong>Duration:</strong> {medicine.duration}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="result-section info">
        <h3>📊 Analysis Summary</h3>
        <ul>
          <li>Entities Detected: {data.entities?.length || 0}</li>
          <li>Medicines Extracted: {extractedMedicines.length}</li>
          <li>PubMed References Found: {data.rag_results?.length || 0}</li>
        </ul>
      </div>
    </div>
  )
}
