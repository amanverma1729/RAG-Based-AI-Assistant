import ReactMarkdown from 'react-markdown'
import { MessageSquare, Menu, Copy, Check } from 'lucide-react'
import { useState } from 'react'
import TypeWriter from './TypeWriter'

export default function ChatArea({ messages, isThinking, chatEndRef, onClearChat, onToggleSidebar, onTypingComplete }) {
  const [copiedIndex, setCopiedIndex] = useState(null)

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
            onClick={onClearChat}
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
            <div className="message-bubble" style={{ position: 'relative' }}>
              {msg.role === 'ai' && msg.isTyping ? (
                <TypeWriter 
                  content={msg.content} 
                  onComplete={() => onTypingComplete(idx)} 
                />
              ) : (
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              )}
              
              {msg.role === 'ai' && !msg.isTyping && (
                <button 
                  onClick={() => handleCopy(msg.content, idx)}
                  style={{
                    position: 'absolute',
                    bottom: '-28px',
                    left: '4px',
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-secondary)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '11px',
                    padding: '4px'
                  }}
                  title="Copy to clipboard"
                >
                  {copiedIndex === idx ? <Check size={14} style={{color: 'var(--accent-green)'}}/> : <Copy size={14} />}
                  {copiedIndex === idx ? <span style={{color: 'var(--accent-green)'}}>Copied</span> : 'Copy'}
                </button>
              )}
            </div>
          </div>
        ))}
        
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
