import './RAGResults.css'

export default function RAGResults({ results, query }) {
  const sources = results || []

  if (sources.length === 0) {
    return (
      <div className="rag-results card">
        <div className="empty-state">
          <p>No sources found for your query yet.</p>
          {query && <p className="query-info">Query: {query}</p>}
        </div>
      </div>
    )
  }

  const getRelevanceColor = (score) => {
    if (score >= 0.8) return '#4CAF50'
    if (score >= 0.6) return '#FFA500'
    if (score >= 0.4) return '#FF9800'
    return '#F44336'
  }

  const getRelevanceBadge = (score) => {
    if (score >= 0.8) return 'Highly Relevant'
    if (score >= 0.6) return 'Relevant'
    if (score >= 0.4) return 'Somewhat Relevant'
    return 'Low Relevance'
  }

  return (
    <div className="rag-results">
      <div className="rag-header">
        <h3>📚 PubMed References</h3>
        <p className="results-count">Found {results.length} relevant articles</p>
      </div>

      <div className="search-query">
        <label>Search Query:</label>
        <p>{query}</p>
      </div>

      <div className="articles-list">
        {sources.map((result, idx) => {
          const score = result.score != null ? result.score : 0.5
          const text = result.text || result.preview || result.snippet || JSON.stringify(result)

          return (
            <article key={idx} className="article-card">
              <div className="article-header">
                <span className="article-num">#{idx + 1}</span>
                <span
                  className="relevance-badge"
                  style={{ borderLeftColor: getRelevanceColor(score) }}
                >
                  {getRelevanceBadge(score)}
                </span>
                <span className="relevance-score">
                  {(score * 100).toFixed(1)}%
                </span>
              </div>

              <div className="article-content">
                <p className="article-text">{text}</p>
              </div>

              <div className="article-footer">
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{
                      width: `${score * 100}%`,
                      backgroundColor: getRelevanceColor(score)
                    }}
                  ></div>
                </div>
              </div>
            </article>
          )
        })}
      </div>

      <div className="rag-info">
        <h4>💡 About PubMed References</h4>
        <p>
          These abstracts and articles are retrieved from PubMed, a database of
          biomedical literature. The relevance score indicates how closely the
          article matches your medical query. Use these references to understand
          the scientific background of your condition and treatment options.
        </p>
      </div>
    </div>
  )
}
