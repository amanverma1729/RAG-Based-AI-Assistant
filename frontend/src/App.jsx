import { useState, useEffect, useRef } from 'react'
import { Send, FileText, Upload, X, Trash2, RefreshCw, MessageSquare } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import './index.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'system',
      content: '🚀 **PDF Intelligence Pro — 100% OFFLINE**\n\n✅ No API Key required\n✅ No Internet required\n✅ Your data stays on your machine\n\n**HOW IT WORKS:**\n1. AI model downloads once (80MB) — then completely offline\n2. Upload 1-5 PDFs from the sidebar\n3. Ask questions — AI finds the relevant content'
    }
  ])
  const [input, setInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [status, setStatus] = useState({ model_loaded: false, ollama_available: false, ollama_model: null })
  const [pdfSlots, setPdfSlots] = useState(Array(5).fill(null))
  
  const chatEndRef = useRef(null)
  const fileInputRef = useRef(null)
  const [uploadSlot, setUploadSlot] = useState(null)

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isThinking])

  useEffect(() => {
    checkStatus()
    // Load model on startup
    fetch(`${API_BASE}/load_model`, { method: 'POST' })
      .then(res => res.json())
      .then(() => checkStatus())
      .catch(err => console.error("Could not load model", err))
  }, [])

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/status`)
      const data = await res.json()
      setStatus(data)
    } catch (e) {
      console.error("Status check failed", e)
    }
  }

  const handleUploadClick = (index) => {
    setUploadSlot(index)
    fileInputRef.current.click()
  }

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (!file || uploadSlot === null) return
    
    // Optimistic UI update
    const newSlots = [...pdfSlots]
    newSlots[uploadSlot] = { loading: true, filename: file.name }
    setPdfSlots(newSlots)

    const formData = new FormData()
    formData.append('slot_index', uploadSlot)
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      if (res.ok) {
        newSlots[uploadSlot] = data.data
        setPdfSlots([...newSlots])
        setMessages(prev => [...prev, {
          role: 'system',
          content: `✅ **PDF ${uploadSlot + 1} ready!**\n📄 ${data.data.filename}\n📃 ${data.data.pages} pages → ${data.data.total_chunks} searchable chunks\n\nYou can now ask questions about this PDF!`
        }])
      } else {
        newSlots[uploadSlot] = null
        setPdfSlots([...newSlots])
        alert(`Upload failed: ${data.detail}`)
      }
    } catch (err) {
      newSlots[uploadSlot] = null
      setPdfSlots([...newSlots])
      alert(`Upload error: ${err.message}`)
    }
    
    // Reset file input
    e.target.value = ''
    setUploadSlot(null)
  }

  const removePdf = async (index) => {
    try {
      await fetch(`${API_BASE}/remove/${index}`, { method: 'DELETE' })
      const newSlots = [...pdfSlots]
      newSlots[index] = null
      setPdfSlots(newSlots)
      setMessages(prev => [...prev, { role: 'system', content: `🗑️ Removed PDF from Slot ${index + 1}.` }])
    } catch (err) {
      console.error(err)
    }
  }

  const clearAllPdfs = async () => {
    try {
      await fetch(`${API_BASE}/clear_all`, { method: 'DELETE' })
      setPdfSlots(Array(5).fill(null))
      setMessages(prev => [...prev, { role: 'system', content: `🗑️ All PDFs removed.` }])
    } catch (err) {
      console.error(err)
    }
  }

  const activeSlots = pdfSlots.map((slot, idx) => slot && !slot.loading ? idx : null).filter(idx => idx !== null)

  const sendMessage = async () => {
    if (!input.trim() || isThinking) return
    
    if (activeSlots.length === 0) {
      alert("Please upload at least one PDF first!")
      return
    }

    const question = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setIsThinking(true)

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          active_slots: activeSlots
        })
      })
      const data = await res.json()
      
      if (res.ok) {
        setMessages(prev => [...prev, { role: 'ai', content: data.answer }])
      } else {
        setMessages(prev => [...prev, { role: 'ai', content: `❌ Error: ${data.detail}` }])
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: `❌ Network Error: Could not connect to API.` }])
    } finally {
      setIsThinking(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div id="root">
      {/* Hidden File Input */}
      <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".pdf" className="hidden" />

      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo-container">
          <FileText className="logo-icon" style={{ color: "var(--accent-blue)" }} />
          <div className="logo-text">
            <h1>PDF Intelligence</h1>
            <p>100% OFFLINE • No API Key</p>
            <div className={`ollama-status ${status.ollama_available ? 'active' : ''}`}>
              {status.ollama_available ? `🦙 Ollama: ${status.ollama_model}` : '🔌 Ollama: Not found'}
            </div>
          </div>
        </div>

        <div className="status-bar" style={{ color: status.model_loaded ? 'var(--accent-green)' : 'var(--accent-orange)' }}>
          {status.model_loaded ? '✅ AI Engine Ready!' : '🔄 Loading AI model...'}
        </div>

        <div className="pdf-slots-header">
          <h2>📁 Load PDFs</h2>
          <span>max 5</span>
        </div>

        <div className="slots-container">
          {pdfSlots.map((slot, index) => (
            <div key={index} className={`pdf-slot ${slot && !slot.loading ? 'active' : ''}`}>
              <div className="slot-badge">{index + 1}</div>
              <div className="slot-info">
                {slot ? (
                  <>
                    <div className="slot-name">{slot.loading ? '⏳ Processing...' : `✓ ${slot.filename}`}</div>
                    <div className="slot-desc">
                      {slot.loading ? 'Extracting & embedding text...' : `${slot.pages} pages • ${slot.total_chunks} chunks`}
                    </div>
                  </>
                ) : (
                  <>
                    <div className="slot-name" style={{ color: 'var(--text-secondary)' }}>Slot {index + 1} — Empty</div>
                    <div className="slot-desc">+ button to upload</div>
                  </>
                )}
              </div>
              <div className="slot-actions">
                {!slot && (
                  <button onClick={() => handleUploadClick(index)} title="Upload PDF">
                    <Upload size={16} style={{ color: `var(--accent-blue)` }} />
                  </button>
                )}
                {slot && !slot.loading && (
                  <button className="remove" onClick={() => removePdf(index)} title="Remove PDF">
                    <X size={16} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', textAlign: 'center' }}>
            {activeSlots.length} / 5 PDFs loaded
          </div>
          <button className="footer-btn danger" onClick={clearAllPdfs}>
            <Trash2 size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: '-2px' }}/>
            Clear All PDFs
          </button>
          <button className="footer-btn" onClick={checkStatus}>
            <RefreshCw size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: '-2px' }}/>
            Recheck Ollama
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-area">
        <div className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <MessageSquare size={18} style={{ color: 'var(--accent-purple)' }}/>
            <h2>AI Chat — Offline Mode</h2>
          </div>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <div style={{ 
              backgroundColor: 'var(--bg-dark)', 
              padding: '6px 14px', 
              borderRadius: '20px', 
              fontSize: '11px', 
              color: isThinking ? 'var(--accent-orange)' : 'var(--accent-green)' 
            }}>
              ⬤ {isThinking ? 'Thinking...' : 'Ready'}
            </div>
            <button 
              className="footer-btn" 
              style={{ padding: '6px 12px', background: 'transparent' }}
              onClick={() => setMessages(messages.slice(0, 1))}
            >
              Clear Chat
            </button>
          </div>
        </div>

        <div className="chat-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className={`sender-label ${msg.role}`}>
                {msg.role === 'user' ? '👤 You' : msg.role === 'ai' ? '🤖 PDF AI' : ''}
              </div>
              <div className="message-bubble">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))}
          
          {isThinking && (
            <div className="message-wrapper ai">
              <div className="sender-label ai">🤖 PDF AI</div>
              <div className="message-bubble" style={{ backgroundColor: 'var(--thinking)', borderColor: 'var(--accent-purple)' }}>
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="input-area">
          <div className="input-container">
            <textarea
              className="input-box"
              placeholder="Type your question here... (Hindi or English)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isThinking}
            />
            <button className="send-btn" onClick={sendMessage} disabled={!input.trim() || isThinking}>
              <Send size={18} />
            </button>
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-secondary)', textAlign: 'center', marginTop: '10px' }}>
            Enter = Send • Shift+Enter = New line • No internet needed!
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
