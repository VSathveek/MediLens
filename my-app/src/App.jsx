import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './App.css'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('results')
  const [conversation, setConversation] = useState([
    {
      role: 'assistant',
      text: 'Hello, I am MediLens. How can I help you with your medical concern today?',
      timestamp: new Date().toISOString(),
    },
  ])
  const [systemPrompt, setSystemPrompt] = useState(
    'You are a helpful, empathetic medical assistant. Answer only medical questions and politely decline general interest queries. Emphasize safety and consulting a healthcare provider.'
  )

  const [isTyping, setIsTyping] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  const backendBase = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'
  const apiBase = backendBase.replace(/\/api$/, '')

  const chatEndRef = useRef(null)

  const formatInlineBold = (text, keyPrefix = '') => {
    const parts = []
    let lastIndex = 0
    const boldRegex = /\*\*([\s\S]+?)\*\*/g
    let match

    while ((match = boldRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index))
      }
      parts.push(<strong key={`${keyPrefix}-bold-${match.index}`}>{match[1]}</strong>)
      lastIndex = match.index + match[0].length
    }

    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex))
    }

    return parts
  }

  // CLEAN THE AI RESPONSE
  const cleanAssistantText = (text) => {
    if (!text) return ''
    // Remove leftover prefix text completely
    const cleaned = text.replace(
      /^(MediLens:)?\s*Here(?:'s| is) a rewritten version of the medical explanation in simple language for a patient:\s*/i,
      ''
    )
    return cleaned.trim()
  }

  const renderAssistantText = (rawText) => {
    const cleanedText = cleanAssistantText(rawText)
    if (!cleanedText) return null

    const lines = cleanedText
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l.length > 0)

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
      const bulletMatch = line.match(/^[\*\-\+]\s+(.+)$/)
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

  const handleProcessInput = async (input) => {
    setLoading(true)
    setIsTyping(true)
    setError(null)
    setResults(null)

    const userTime = new Date().toISOString()
    const newMessage = { role: 'user', text: input, timestamp: userTime }

    setConversation((prev) => [...prev, newMessage])

    try {
      // Merge previous conversation for context
      const fullQuestion = [...conversation, newMessage]
        .map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.text}`)
        .join('\n\n')

      const res = await fetch(`${apiBase}/api/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: fullQuestion,
          system_prompt: systemPrompt,
        }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(`Server error ${res.status}: ${text}`)
      }

      const data = await res.json()
      const answer = data.answer || data.reasoning || data.medical_query || 'No response.'
      const assistantText = Array.isArray(answer) ? answer.join('\n') : String(answer)

      setConversation((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: assistantText,
          sources: data.references || data.rag_results || [],
          timestamp: new Date().toISOString(),
        },
      ])

      setResults(data)
      setActiveTab('results')
    } catch (err) {
      setError(err.message || 'Failed to process request')
      setConversation((prev) => [
        ...prev,
        { role: 'assistant', text: 'Something went wrong. Try again.', timestamp: new Date().toISOString() },
      ])
    } finally {
      setLoading(false)
      setIsTyping(false)
    }
  }

  const [inputText, setInputText] = useState('')

  const handleSend = () => {
    const text = inputText.trim()
    if (!text) return
    handleProcessInput(text)
    setInputText('')
  }

  const handleNewChat = () => {
    setConversation([
      {
        role: 'assistant',
        text: 'Hello, I am MediLens. How can I help you with your medical concern today?',
        timestamp: new Date().toISOString(),
      },
    ])
    setResults(null)
    setError(null)
    setInputText('')
    window.localStorage.removeItem('medilens_chat')
  }

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">
          <div className="logo-icon"></div>
        </div>

        <div className="newchat" onClick={handleNewChat}>
          + New Chat
        </div>

        <div className="chatlist">
          <div className="chatitem">Welcome</div>
          <div className="chatitem">Medical help</div>
          <div className="chatitem">Prescription review</div>
        </div>
      </div>

      <div className="main">
        <div className="header">Medical AI Chat</div>

        <div className="messages">
          {conversation.map((m, idx) => (
            <div key={idx} className="message">
              <div className={`avatar ${m.role === 'user' ? 'user' : 'bot'}`}>
                {m.role === 'user' ? 'U' : 'AI'}
              </div>

              <div className="text">
                <strong>{m.role === 'user' ? 'You' : 'MediLens'}:</strong>
                {m.role === 'assistant' ? renderAssistantText(m.text) : ` ${m.text}`}

                {m.sources?.length > 0 && (
                  <div className="chat-sources">
                    <strong>Sources:</strong>
                    <ul>
                      {m.sources.map((src, sidx) => {
                        const sourceText =
                          typeof src === 'string'
                            ? src
                            : src?.text || src?.snippet || JSON.stringify(src)
                        const trimmed = sourceText.length > 170 ? `${sourceText.slice(0, 170)}...` : sourceText
                        return (
                          <li key={`src-${sidx}`} className="source-item">
                            {trimmed}
                          </li>
                        )
                      })}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="message typing">
              <div className="avatar bot">AI</div>
              <div className="text">Typing...</div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <div className="input-area">
          <div className="inputbox">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={1}
              placeholder="Message AI..."
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
            />
            <button
              className="send"
              onClick={handleSend}
              disabled={loading || !inputText.trim()}
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
          <div className="disclaimer">
            AI responses may contain mistakes. Verify important information.
          </div>
        </div>
      </div>
    </div>
  )
}

export default App