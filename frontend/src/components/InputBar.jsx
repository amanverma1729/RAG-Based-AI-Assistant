import React, { useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

export default function InputBar({ input, setInput, isThinking, onSendMessage }) {
  const textareaRef = useRef(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`
    }
  }, [input])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSendMessage()
    }
  }

  return (
    <div className="input-area">
      <div className="input-container">
        <textarea
          ref={textareaRef}
          className="input-box"
          placeholder="Ask a question about your PDFs..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isThinking}
          rows={1}
        />
        <button 
          className="send-btn" 
          onClick={onSendMessage}
          disabled={!input.trim() || isThinking}
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}