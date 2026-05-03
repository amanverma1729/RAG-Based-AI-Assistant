import { FileText, Upload, X, Trash2, RefreshCw } from 'lucide-react'

export default function Sidebar({
  status,
  pdfSlots,
  activeSlots,
  onUploadClick,
  onRemovePdf,
  onClearAll,
  onRecheckStatus,
  isOpen,
  onClose
}) {
  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="logo-container">
        <FileText className="logo-icon" style={{ color: "var(--accent-blue)" }} />
        <div className="logo-text" style={{ flex: 1 }}>
          <h1>PDF Intelligence</h1>
          <p>100% OFFLINE • No API Key</p>
          <div className={`ollama-status ${status.ollama_available ? 'active' : ''}`}>
            {status.ollama_available ? `🦙 Ollama: ${status.ollama_model}` : '🔌 Ollama: Not found'}
          </div>
        </div>
        <button 
          className="mobile-toggle-btn" 
          onClick={onClose}
        >
          <X size={20} />
        </button>
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
                <button onClick={() => onUploadClick(index)} title="Upload PDF">
                  <Upload size={16} style={{ color: `var(--accent-blue)` }} />
                </button>
              )}
              {slot && !slot.loading && (
                <button className="remove" onClick={() => onRemovePdf(index)} title="Remove PDF">
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
        <button className="footer-btn danger" onClick={onClearAll}>
          <Trash2 size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: '-2px' }}/>
          Clear All PDFs
        </button>
        <button className="footer-btn" onClick={onRecheckStatus}>
          <RefreshCw size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: '-2px' }}/>
          Recheck Ollama
        </button>
      </div>
    </div>
  )
}
