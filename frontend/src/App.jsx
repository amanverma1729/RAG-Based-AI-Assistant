import { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import InputBar from './components/InputBar'
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

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
        setMessages(prev => [...prev, { role: 'ai', content: data.answer, isTyping: true }])
      } else {
        setMessages(prev => [...prev, { role: 'ai', content: `❌ Error: ${data.detail}` }])
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: `❌ Network Error: Could not connect to API.` }])
    } finally {
      setIsThinking(false)
    }
  }

  return (
    <div id="root">
      {/* Hidden File Input */}
      <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".pdf" className="hidden" />
      {/* Sidebar Overlay */}
      <div 
        className={`sidebar-overlay ${isSidebarOpen ? 'open' : ''}`}
        onClick={() => setIsSidebarOpen(false)}
      ></div>

      <Sidebar 
        status={status}
        pdfSlots={pdfSlots}
        activeSlots={activeSlots}
        onUploadClick={handleUploadClick}
        onRemovePdf={removePdf}
        onClearAll={clearAllPdfs}
        onRecheckStatus={checkStatus}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      <div className="main-area">
        <ChatArea 
          messages={messages}
          isThinking={isThinking}
          chatEndRef={chatEndRef}
          onClearChat={() => setMessages(messages.slice(0, 1))}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          onTypingComplete={(idx) => setMessages(prev => {
            const newMsgs = [...prev];
            if(newMsgs[idx]) newMsgs[idx].isTyping = false;
            return newMsgs;
          })}
        />
        <InputBar 
          input={input}
          setInput={setInput}
          isThinking={isThinking}
          onSendMessage={sendMessage}
        />
      </div>
    </div>
  )
}

export default App
