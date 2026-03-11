import './EntityDisplay.css'

export default function EntityDisplay({ entities }) {
  if (!entities || entities.length === 0) {
    return (
      <div className="entity-display">
        <div className="empty-state">
          <p>No medical entities detected in the input.</p>
        </div>
      </div>
    )
  }

  // Group entities by type
  const groupedEntities = {}
  entities.forEach(entity => {
    const type = entity.entity_group || entity.entity || 'OTHER'
    if (!groupedEntities[type]) {
      groupedEntities[type] = []
    }
    groupedEntities[type].push(entity)
  })

  const entityTypeColors = {
    'DISEASE': '#FF6B6B',
    'CHEMICAL': '#4ECDC4',
    'PROTEIN': '#45B7D1',
    'BODY_PART': '#96CEB4',
    'OTHER': '#CCCCCC'
  }

  const entityTypeEmojis = {
    'DISEASE': '🦠',
    'CHEMICAL': '⚗️',
    'PROTEIN': '🧬',
    'BODY_PART': '🫀',
    'OTHER': '📌'
  }

  return (
    <div className="entity-display">
      <div className="entity-stats">
        <p>Found <strong>{entities.length}</strong> medical entities</p>
      </div>

      <div className="entity-groups">
        {Object.entries(groupedEntities).map(([type, typeEntities]) => (
          <div key={type} className="entity-group">
            <h4 className="group-title">
              {entityTypeEmojis[type] || '📌'} {type}
              <span className="count">{typeEntities.length}</span>
            </h4>
            <div className="entities-list">
              {typeEntities.map((entity, idx) => (
                <div
                  key={idx}
                  className="entity-tag"
                  style={{
                    borderLeftColor: entityTypeColors[type] || entityTypeColors['OTHER']
                  }}
                >
                  <span className="entity-word">{entity.word || entity.text}</span>
                  {entity.score && (
                    <span className="entity-score">
                      {(entity.score * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="entity-legend">
        <h4>Entity Types</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#FF6B6B' }}></span>
            <span>Disease/Condition</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#4ECDC4' }}></span>
            <span>Chemical/Drug</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#45B7D1' }}></span>
            <span>Protein/Gene</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#96CEB4' }}></span>
            <span>Body Parts</span>
          </div>
        </div>
      </div>
    </div>
  )
}
