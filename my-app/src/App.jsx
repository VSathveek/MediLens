import { useEffect, useRef, useState } from 'react'
import './App.css'

const WELCOME_MESSAGE = {
  role: 'assistant',
  text: "Hi, I'm MediLens. Tell me about your symptoms, medications, or upload a prescription photo, and I'll help you understand it.",
  timestamp: new Date().toISOString(),
}

const DEFAULT_SYSTEM_PROMPT =
  'You are a helpful, empathetic medical assistant. Answer only medical questions and politely decline general interest queries. Emphasize safety and consulting a healthcare provider.'

function App() {
  const [conversation, setConversation] = useState([WELCOME_MESSAGE])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState(null)
  const [systemPrompt, setSystemPrompt] = useState(DEFAULT_SYSTEM_PROMPT)
  const [showSettings, setShowSettings] = useState(false)

  const backendBase = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
  const apiBase = backendBase.replace(/\/$/, '')

  const chatEndRef = useRef(null)
  const fileInputRef = useRef(null)
  const textareaRef = useRef(null)

  const formatInlineBold = (text, keyPrefix = '') => {
    const parts = []
    let lastIndex = 0
    const boldRegex = /\*\*([\s\S]+?)\*\*/g
    let match

    while ((match = boldRegex.exec(text)) !== null) {
      if (match.index > lastIndex) parts.push(text.slice(lastIndex, match.index))
      parts.push(<strong key={`${keyPrefix}-bold-${match.index}`}>{match[1]}</strong>)
      lastIndex = match.index + match[0].length
    }
    if (lastIndex < text.length) parts.push(text.slice(lastIndex))
    return parts
  }

  const renderAssistantText = (rawText) => {
    if (!rawText) return null
    const lines = rawText.split(/\r?\n/).map((l) => l.trim()).filter(Boolean)

    const result = []
    let listItems = []

    const flushList = () => {
      if (listItems.length > 0) {
        result.push(
          <ul className="assistant-list" key={`list-${result.length}`}>
            {listItems}
          </ul>
        )
        listItems = []
      }
    }

    lines.forEach((line, idx) => {
      const bulletMatch = line.match(/^[*\-+]\s+(.+)$/)
      if (bulletMatch) {
        listItems.push(
          <li className="assistant-list-item" key={`li-${idx}`}>
            {formatInlineBold(bulletMatch[1], `li-${idx}`)}
          </li>
        )
      } else {
        flushList()
        result.push(
          <p className="assistant-paragraph" key={`p-${idx}`}>
            {formatInlineBold(line, `p-${idx}`)}
          </p>
        )
      }
    })
    flushList()
    return <>{result}</>
  }

  useEffect(() => {
    const savedChat = window.localStorage.getItem('medilens_chat')
    const savedSystemPrompt = window.localStorage.getItem('medilens_system_prompt')
    if (savedChat) setConversation(JSON.parse(savedChat))
    if (savedSystemPrompt) setSystemPrompt(savedSystemPrompt)
  }, [])

  useEffect(() => {
    window.localStorage.setItem('medilens_chat', JSON.stringify(conversation))
    window.localStorage.setItem('medilens_system_prompt', systemPrompt)
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation, systemPrompt])

  const appendAssistantReply = (data) => {
    setConversation((prev) => [
      ...prev,
      {
        role: 'assistant',
        text: data.answer || 'No response.',
        sources: data.references || [],
        timestamp: new Date().toISOString(),
      },
    ])
  }

  const appendAssistantError = (message) => {
    setError(message)
    setConversation((prev) => [
      ...prev,
      { role: 'assistant', text: 'Something went wrong. Please try again.', timestamp: new Date().toISOString() },
    ])
  }

  const handleSend = async () => {
    const text = inputText.trim()
    if (!text || loading) return

    setInputText('')
    setLoading(true)
    setIsTyping(true)
    setError(null)
    setConversation((prev) => [...prev, { role: 'user', text, timestamp: new Date().toISOString() }])

    try {
      const res = await fetch(`${apiBase}/api/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, system_prompt: systemPrompt }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `Server error ${res.status}`)
      }
      appendAssistantReply(await res.json())
    } catch (err) {
      appendAssistantError(err.message)
    } finally {
      setLoading(false)
      setIsTyping(false)
    }
  }

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file || loading) return

    setLoading(true)
    setIsTyping(true)
    setError(null)
    setConversation((prev) => [
      ...prev,
      { role: 'user', text: `📎 Uploaded prescription image: ${file.name}`, timestamp: new Date().toISOString() },
    ])

    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${apiBase}/api/upload`, { method: 'POST', body: formData })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `Server error ${res.status}`)
      }
      appendAssistantReply(await res.json())
    } catch (err) {
      appendAssistantError(err.message)
    } finally {
      setLoading(false)
      setIsTyping(false)
    }
  }

  const handleNewChat = () => {
    setConversation([WELCOME_MESSAGE])
    setError(null)
    setInputText('')
    window.localStorage.removeItem('medilens_chat')
  }

  const handleTextareaInput = (e) => {
    setInputText(e.target.value)
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`
    }
  }

  const isFreshChat = conversation.length === 1

  return (
    <div className="app">
      <header className="topbar">
        <div className="wordmark">MediLens</div>
        <div className="topbar-actions">
          <a className="pill pill-ghost" href="/rag-internals.html">
            How it works
          </a>
          <button className="pill pill-ghost" onClick={() => setShowSettings((v) => !v)}>
            {showSettings ? 'Hide settings' : 'Settings'}
          </button>
          <button className="pill pill-outline" onClick={handleNewChat}>
            New chat
          </button>
        </div>
      </header>

      {showSettings && (
        <div className="settings-panel">
          <label htmlFor="system-prompt">Assistant persona / system prompt</label>
          <textarea
            id="system-prompt"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={3}
          />
        </div>
      )}

      <main className="main">
        {isFreshChat ? (
          <div className="hero">
            <h1 className="hero-title">Understand your health, clearly.</h1>
            <p className="hero-subtitle">{WELCOME_MESSAGE.text}</p>
          </div>
        ) : (
          <div className="messages">
            {conversation.map((m, idx) => (
              <div key={idx} className={`message message-${m.role}`}>
                {m.role === 'assistant' && <div className="avatar">AI</div>}
                <div className={m.role === 'user' ? 'bubble-user' : 'bubble-assistant'}>
                  {m.role === 'assistant' ? renderAssistantText(m.text) : m.text}

                  {m.sources?.length > 0 && (
                    <div className="sources">
                      <div className="sources-label">References</div>
                      <div className="sources-list">
                        {m.sources.map((src, sidx) => {
                          const sourceText = typeof src === 'string' ? src : src?.text || JSON.stringify(src)
                          const trimmed = sourceText.length > 180 ? `${sourceText.slice(0, 180)}...` : sourceText
                          return (
                            <div key={`src-${sidx}`} className="source-card">
                              {trimmed}
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="message message-assistant">
                <div className="avatar">AI</div>
                <div className="bubble-assistant typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        )}

        {error && <div className="error-banner">{error}</div>}

        <div className="input-area">
          <div className="input-shell">
            <button
              className="icon-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              title="Upload prescription image"
              aria-label="Upload prescription image"
            >
              +
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={handleFileSelect}
            />
            <textarea
              ref={textareaRef}
              value={inputText}
              onChange={handleTextareaInput}
              rows={1}
              placeholder="Describe your symptoms, ask about a medication..."
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
            />
            <button className="pill pill-send" onClick={handleSend} disabled={loading || !inputText.trim()}>
              {loading ? 'Sending' : 'Send'}
            </button>
          </div>
          <div className="disclaimer">
            MediLens is an educational tool, not a substitute for professional medical advice.
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
