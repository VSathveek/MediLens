import { useState, useRef } from 'react'
import './InputForm.css'

export default function InputForm({ onProcessText, onUploadPrescription, loading }) {
  const [textInput, setTextInput] = useState('')
  const [inputMode, setInputMode] = useState('text')
  const fileInputRef = useRef(null)

  const handleTextSubmit = (e) => {
    e.preventDefault()
    if (textInput.trim()) {
      onProcessText(textInput)
      setTextInput('')
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      onUploadPrescription(file)
    }
  }

  return (
    <div className="input-form">
      <div className="mode-selector">
        <button
          className={`mode-btn ${inputMode === 'text' ? 'active' : ''}`}
          onClick={() => setInputMode('text')}
          disabled={loading}
        >
          📝 Text Input
        </button>
        <button
          className={`mode-btn ${inputMode === 'image' ? 'active' : ''}`}
          onClick={() => setInputMode('image')}
          disabled={loading}
        >
          📷 Upload Prescription
        </button>
      </div>

      {inputMode === 'text' && (
        <form onSubmit={handleTextSubmit} className="text-form">
          <div className="form-group">
            <label htmlFor="text-input">Describe your medical concern or question:</label>
            <textarea
              id="text-input"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="e.g., I have severe headache and fever for 2 days. What could be the cause? What medicines should I take?"
              rows="4"
              disabled={loading}
              maxLength={1000}
            />
            <div className="char-count">{textInput.length}/1000</div>
          </div>
          <button
            type="submit"
            className="submit-btn"
            disabled={!textInput.trim() || loading}
          >
            {loading ? '⏳ Processing...' : '🔍 Analyze'}
          </button>
        </form>
      )}

      {inputMode === 'image' && (
        <div className="image-form">
          <div
            className="upload-area"
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault()
              handleFileSelect({ target: { files: e.dataTransfer.files } })
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              disabled={loading}
            />
            <div className="upload-content">
              <p className="upload-icon">📸</p>
              <p className="upload-text">Drag and drop your prescription image here</p>
              <p className="upload-subtext">or click to select a file</p>
            </div>
          </div>
          <p className="upload-hint">
            Supported formats: JPG, PNG | Max size: 10MB
          </p>
        </div>
      )}

      <div className="tips">
        <h4>💡 Tips for best results:</h4>
        <ul>
          <li>Provide clear, detailed medical information</li>
          <li>Mention symptoms, duration, and any medications currently taking</li>
          <li>For prescriptions, ensure the text is clearly visible in the image</li>
          <li>The system will analyze your input and provide medical references</li>
        </ul>
      </div>
    </div>
  )
}
