import { Send } from 'lucide-react'

export default function InputBar({ input, setInput, isThinking, onSendMessage }) {
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
          className="input-box"
          placeholder="Type your question here... (Hindi or English)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isThinking}
        />
        <button 
          className="send-btn" 
          onClick={onSendMessage} 
          disabled={!input.trim() || isThinking}
        >
          <Send size={18} />
        </button>
      </div>
      <div style={{ fontSize: '10px', color: 'var(--text-secondary)', textAlign: 'center', marginTop: '10px' }}>
        Enter = Send • Shift+Enter = New line • No internet needed!
      </div>
    </div>
  )
}
