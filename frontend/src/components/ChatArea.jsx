import ReactMarkdown from 'react-markdown'
import { MessageSquare, Menu, Copy, Check } from 'lucide-react'
import { useState } from 'react'
import TypeWriter from './TypeWriter'

export default function ChatArea({ messages, isThinking, chatEndRef, onClearChat, onToggleSidebar, onTypingComplete }) {
  const [copiedIndex, setCopiedIndex] = useState(null)

  // 🌐 Detect Hindi or English
  const detectLanguage = (text) => {
    const hindiRegex = /[\u0900-\u097F]/
    return hindiRegex.test(text) ? "Hindi" : "English"
  }

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  return (
    <>
      <div className="topbar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            className="mobile-toggle-btn"
            onClick={onToggleSidebar}
          >
            <Menu size={20} />
          </button>
          <MessageSquare size={18} style={{ color: 'var(--accent-purple)' }} />
          <h2>RAG AI Assistant</h2>
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
            onClick={onClearChat}
          >
            Clear Chat
          </button>
        </div>
      </div>

      <div className="chat-container">
        {messages.map((msg, idx) => {
          const lang = detectLanguage(msg.content)

          return (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <div className={`sender-label ${msg.role}`} style={{ marginBottom: 0 }}>
                  {msg.role === 'user' ? '👤 You' : msg.role === 'ai' ? '🤖 PDF AI' : '⚙️ System'}
                </div>
                {/* 🌐 Language badge (NEW) */}
                {msg.role === 'ai' && (
                  <div style={{
                    fontSize: '10px',
                    color: 'var(--text-secondary)',
                    background: 'var(--bg-dark)',
                    padding: '2px 8px',
                    borderRadius: '10px'
                  }}>
                    🌐 {lang}
                  </div>
                )}
              </div>

              <div className="message-bubble">
                {/* ✨ Existing logic (UNCHANGED) */}
                {msg.role === 'ai' && msg.isTyping ? (
                  <TypeWriter
                    content={msg.content}
                    onComplete={() => onTypingComplete(idx)}
                  />
                ) : (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                )}
              </div>

              {/* 📋 Copy button */}
              {msg.role === 'ai' && !msg.isTyping && (
                <button
                  onClick={() => handleCopy(msg.content, idx)}
                  style={{
                    marginTop: '6px',
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-secondary)',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '11px',
                    padding: '2px 4px'
                  }}
                  title="Copy to clipboard"
                >
                  {copiedIndex === idx
                    ? <Check size={14} style={{ color: 'var(--accent-green)' }} />
                    : <Copy size={14} />
                  }
                  {copiedIndex === idx
                    ? <span style={{ color: 'var(--accent-green)' }}>Copied</span>
                    : 'Copy'
                  }
                </button>
              )}
            </div>
          )
        })}

        {isThinking && (
          <div className="message-wrapper ai">
            <div className="sender-label ai">🤖 PDF AI</div>
            <div className="message-bubble">
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
    </>
  )
}