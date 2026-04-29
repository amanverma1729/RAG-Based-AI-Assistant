import React, { useState, useRef, useEffect } from 'react';
import { Paperclip, ArrowUp, Square, FileText, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Message from './Message';

const useIntelligentScroll = (isStreaming, messages) => {
  const scrollRef = useRef(null);
  const [isScrolledUp, setIsScrolledUp] = useState(false);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;

    const handleScroll = () => {
      const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
      setIsScrolledUp(!isNearBottom);
    };

    el.addEventListener('scroll', handleScroll);
    return () => el.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (!isScrolledUp && isStreaming && scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages, isStreaming, isScrolledUp]);

  return scrollRef;
};

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [attachment, setAttachment] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [isRetrievingContext, setIsRetrievingContext] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setAttachment(e.target.files[0]);
    }
  };

  const removeAttachment = () => {
    setAttachment(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const scrollRef = useIntelligentScroll(isTyping || isRetrievingContext, messages);

  useEffect(() => {
    const handleGlobalKeys = (e) => {
      if (e.key === 'Escape' && (isTyping || isRetrievingContext)) {
        setIsTyping(false);
        setIsRetrievingContext(false);
      }
    };
    window.addEventListener('keydown', handleGlobalKeys);
    return () => window.removeEventListener('keydown', handleGlobalKeys);
  }, [isTyping, isRetrievingContext]);

  const handleInput = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
  };

  const [isResearchMode, setIsResearchMode] = useState(false);
  const [isComparing, setIsComparing] = useState(false);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if ((!input.trim() && !attachment) || isTyping || isRetrievingContext || isComparing) return;

    const queryText = input.trim();
    const userMsg = { id: Date.now(), role: 'user', content: queryText };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    removeAttachment();
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    
    // --- RESEARCH MODE (SIDE-BY-SIDE) ---
    if (isResearchMode) {
      setIsComparing(true);
      try {
        const response = await fetch('http://localhost:8000/api/v1/chat/compare', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: queryText,
            owner_id: "123e4567-e89b-12d3-a456-426614174000"
          })
        });
        const data = await response.json();
        
        setMessages(prev => [...prev, {
          id: Date.now() + 5,
          role: 'assistant',
          isComparison: true,
          content: `### 🧪 Research Comparison\n\n**RAG Impact:** ${data.comparison_metrics.rag_benefit}\n**Knowledge Delta:** ${data.comparison_metrics.grounding_delta}\n\n---\n\n#### [Variant A: With RAG]\n${data.rag_answer}\n\n#### [Variant B: Baseline (No-RAG)]\n${data.baseline_answer}`,
          sources: data.sources.map((id, i) => ({ title: `Context Chunk ${i+1}`, snippet: `ID: ${id}` })),
          model: 'GPT-4o (Research)'
        }]);
      } catch (err) {
        console.error("Comparison Error:", err);
      } finally {
        setIsComparing(false);
      }
      return;
    }

    // --- STANDARD MULTIMODAL STREAMING ---
    setIsRetrievingContext(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          owner_id: "123e4567-e89b-12d3-a456-426614174000"
        })
      });

      if (!response.ok) throw new Error("Backend unreachable");
      
      setIsRetrievingContext(false);
      setIsTyping(true);

      const assistantId = Date.now() + 1;
      setMessages(prev => [...prev, { 
        id: assistantId, 
        role: 'assistant', 
        content: '', 
        sources: [],
        model: 'GPT-4o'
      }]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let fullContent = "";
      let sourcesList = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunks = decoder.decode(value, { stream: true }).split('\n\n');
        for (const chunk of chunks) {
          if (!chunk.startsWith('data: ')) continue;
          const dataStr = chunk.replace('data: ', '').trim();
          
          if (dataStr === '[DONE]') {
            setIsTyping(false);
            setMessages(prev => prev.map(m => m.id === assistantId ? {...m, content: fullContent, sources: sourcesList} : m));
            break;
          }

          try {
            const parsed = JSON.parse(dataStr);
            if (parsed.type === 'sources') {
              sourcesList = parsed.data.map((id, index) => ({
                title: `pgvector chunk [${index + 1}]`,
                snippet: `Semantic context retrieved successfully under ID: ${id}`
              }));
              setMessages(prev => prev.map(m => m.id === assistantId ? {...m, sources: sourcesList} : m));
            } else if (parsed.type === 'token') {
              fullContent += parsed.data;
              setMessages(prev => prev.map(m => m.id === assistantId ? {...m, content: fullContent + '<span class="streaming-cursor"></span>'} : m));
            } else if (parsed.type === 'image') {
              setMessages(prev => prev.map(m => m.id === assistantId ? {...m, imageUrl: parsed.data, content: 'Research Visualization Generated:'} : m));
              setIsTyping(false);
            } else if (parsed.type === 'status') {
              setMessages(prev => prev.map(m => m.id === assistantId ? {...m, content: `_${parsed.data}_`} : m));
            }
          } catch (e) {}
        }
      }
    } catch (error) {
      setIsRetrievingContext(false);
      setIsTyping(false);
      setMessages(prev => [...prev, { id: Date.now()+2, role: 'assistant', content: '**Error:** Check backend connectivity.', model: 'System' }]);
    }
  };

  return (
    <>
      <div className="flex-1 w-full flex flex-col h-full overflow-hidden absolute inset-0 pb-[120px]">
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8 pt-10 pb-12 w-full max-w-3xl mx-auto space-y-6">
          
          {/* Empty State Presentation */}
          {messages.length === 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center mt-10 md:mt-24 text-center"
            >
              <div className="w-16 h-16 rounded-full flex items-center justify-center mb-6 border border-border-active">
                 <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-text-primary">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                 </svg>
              </div>
              <h1 className="text-2xl font-semibold text-text-primary mb-2">RAG Assistant</h1>
              <p className="text-text-secondary text-md mb-8">Ask questions from your documents</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                {[
                  { text: "Explain the deployment pipeline" },
                  { text: "Search architecture documents" },
                  { text: "Generate an image of a cloud network" },
                  { text: "Help me write a Python script" }
                ].map((s, i) => (
                  <button key={i} onClick={() => setInput(s.text)} className="flex items-center p-3.5 bg-transparent hover:bg-surface-card border border-border-active rounded-xl transition-all shadow-sm text-sm text-text-secondary hover:text-text-primary">
                    {s.text}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          <AnimatePresence initial={false}>
            {messages.map((msg, index) => (
              <Message 
                key={msg.id} 
                role={msg.role} 
                content={msg.content} 
                sources={msg.sources} 
                model={msg.model} 
                imageUrl={msg.imageUrl}
                isComparison={msg.isComparison}
                isRetrievingContext={(isRetrievingContext || isComparing) && index === messages.length - 1 && msg.role === 'user' ? true : false}
              />
            ))}
            
            {(isRetrievingContext || isComparing) && (
               <Message 
                 key="skeleton-loading" 
                 role="assistant" 
                 content="" 
                 model="GPT-4o"
                 isRetrievingContext={true}
               />
            )}
          </AnimatePresence>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 w-full px-4 pb-6 flex justify-center pointer-events-none z-20">
        <div className="w-full max-w-3xl relative pointer-events-auto flex flex-col">
          
          <motion.form 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            onSubmit={handleSubmit} 
            className="relative flex flex-col gap-2 bg-surface-card rounded-[24px] p-2 w-full focus-within:ring-0 focus-within:border-transparent transition-all shadow-[0_0_15px_rgba(0,0,0,0.1)]"
          >
            {/* Attachment Preview rendering */}
            {attachment && (
              <div className="relative mx-3 mt-2 flex items-center gap-3 bg-surface-base border border-border-active rounded-xl p-2 w-max max-w-full sm:max-w-[300px] group shadow-sm">
                <div className="w-8 h-8 rounded-lg bg-surface-sidebar flex items-center justify-center text-text-primary shrink-0">
                  <FileText size={16} />
                </div>
                <div className="flex flex-col min-w-0 pr-6">
                  <span className="text-sm font-semibold text-text-primary truncate">{attachment.name}</span>
                  <span className="text-[10px] text-text-tertiary uppercase tracking-wider">{(attachment.size / 1024).toFixed(1)} KB</span>
                </div>
                <button 
                  type="button" 
                  onClick={removeAttachment}
                  className="absolute p-1 top-2 right-2 text-text-tertiary hover:text-text-primary bg-surface-base rounded-md transition-colors"
                >
                  <X size={14} strokeWidth={2.5} />
                </button>
              </div>
            )}
            
            <div className="relative flex items-end gap-2 w-full px-2">
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                className="hidden" 
                accept=".pdf,.txt,.docx,.csv"
              />
              <button 
                type="button" 
                onClick={() => fileInputRef.current?.click()}
                className="p-2 mb-1.5 text-text-secondary hover:text-text-primary rounded-xl transition-colors shrink-0 bg-transparent"
              >
                <Paperclip size={20} strokeWidth={2} />
              </button>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInput}
                placeholder="Message RAG Assistant..."
                className="w-full bg-transparent border-0 py-3.5 text-[15px] focus:outline-none focus:ring-0 text-text-primary resize-none placeholder-text-secondary leading-relaxed max-h-[200px]"
                rows="1"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />
              <button 
                type={(isTyping || isRetrievingContext || isComparing) ? "button" : "submit"} 
                className={`p-2 mb-1.5 shrink-0 rounded-xl flex items-center justify-center transition-all duration-200 ${
                  (isTyping || isRetrievingContext || isComparing)
                  ? "bg-transparent text-text-primary" 
                  : (input.trim() || attachment) 
                    ? "bg-white text-black hover:bg-gray-200" 
                    : "bg-surface-hover text-text-secondary cursor-not-allowed"
                }`}
                disabled={!(input.trim() || attachment) && !(isTyping || isRetrievingContext || isComparing)}
              >
                {(isTyping || isRetrievingContext || isComparing) ? <Square fill="currentColor" size={16} /> : <ArrowUp size={18} strokeWidth={2.5} />}
              </button>
            </div>
          </motion.form>
          <div className="text-center mt-2 text-[11px] text-text-secondary">
            RAG Assistant can make mistakes. Consider verifying important information.
          </div>
        </div>
      </div>
    </>
  );
}
