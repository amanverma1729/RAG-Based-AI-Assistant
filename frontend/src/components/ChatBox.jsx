import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Paperclip, ArrowUp, Square, Terminal, Search, Zap, X, FileText } from 'lucide-react';
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
  const [messages, setMessages] = useState([]); // Empty state by default
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
      <div className="flex-1 w-full flex flex-col h-full overflow-hidden absolute inset-0 pb-[160px]">
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8 pt-8 pb-12 space-y-10">
          
          {/* Empty State Presentation */}
          {messages.length === 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto pt-20"
            >
              <div className="w-16 h-16 bg-surface-sidebar rounded-2xl flex items-center justify-center mb-6 shadow-lg border border-border-light drop-shadow-xl">
                <Sparkles size={32} className="text-accent-iris" />
              </div>
              <h1 className="text-3xl font-bold text-text-primary mb-3">How can I help you today?</h1>
              <p className="text-text-tertiary mb-10 text-lg">I have access to your organization's internal knowledge base.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
                {[
                  { icon: <Terminal size={18}/>, text: "Explain the deployment pipeline" },
                  { icon: <Search size={18}/>, text: "Search architecture documents" },
                  { icon: <Zap size={18}/>, text: "Generate an image of a cloud network" }
                ].map((s, i) => (
                  <button key={i} onClick={() => setInput(s.text)} className="flex flex-col items-start p-4 bg-surface-sidebar hover:bg-surface-hover/50 border border-border-light rounded-xl transition-all shadow-sm group">
                    <div className="text-accent-iris bg-accent-iris/10 p-2 rounded-lg mb-3 group-hover:scale-110 transition-transform">{s.icon}</div>
                    <span className="text-sm font-medium text-text-secondary text-left">{s.text}</span>
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

      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-surface-base via-surface-base to-transparent px-4 pb-8 pt-12 flex justify-center pointer-events-none z-20">
        <div className="w-full max-w-3xl relative pointer-events-auto flex flex-col items-center">
          
          {/* Research Mode Toggle */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2 mb-4 bg-surface-sidebar border border-border-light px-3 py-1.5 rounded-full shadow-lg"
          >
            <div className={`w-2 h-2 rounded-full ${isResearchMode ? 'bg-accent-iris animate-pulse' : 'bg-text-tertiary'}`}></div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-text-secondary">Research Mode</span>
            <button 
              onClick={() => setIsResearchMode(!isResearchMode)}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${isResearchMode ? 'bg-accent-iris' : 'bg-surface-hover'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isResearchMode ? 'translate-x-4' : 'translate-x-1'}`} />
            </button>
          </motion.div>

          <motion.form 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            onSubmit={handleSubmit} 
            className="relative flex flex-col gap-2 bg-surface-sidebar border border-border-light shadow-2xl rounded-2xl p-3 w-full ring-1 ring-inset ring-transparent focus-within:ring-accent-iris/40 focus-within:border-accent-iris/40 transition-all drop-shadow-2xl"
          >
            {/* Attachment Preview rendering */}
            {attachment && (
              <div className="relative mx-1 mt-1 flex items-center gap-3 bg-surface-base border border-border-light rounded-xl p-2.5 w-max max-w-full sm:max-w-[300px] group animate-fade-in shadow-sm">
                <div className="w-8 h-8 rounded-lg bg-accent-iris/10 flex items-center justify-center text-accent-iris shrink-0">
                  <FileText size={16} />
                </div>
                <div className="flex flex-col min-w-0 pr-6">
                  <span className="text-sm font-semibold text-text-primary truncate">{attachment.name}</span>
                  <span className="text-[10px] text-text-tertiary uppercase tracking-wider">{(attachment.size / 1024).toFixed(1)} KB</span>
                </div>
                <button 
                  type="button" 
                  onClick={removeAttachment}
                  className="absolute p-1 top-2 right-2 text-text-tertiary hover:text-red-400 bg-surface-hover/80 rounded-md transition-colors shadow-sm"
                >
                  <X size={12} strokeWidth={3} />
                </button>
              </div>
            )}
            
            <div className="relative flex items-end gap-3 w-full">
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
                className="p-2.5 mb-0.5 text-text-tertiary hover:text-text-primary hover:bg-surface-hover/80 rounded-xl transition-colors shrink-0 bg-surface-base border border-border-light shadow-sm"
              >
                <Paperclip size={18} />
              </button>
              <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInput}
              placeholder={isResearchMode ? "Run comparative research query..." : "Ask anything or upload a document..."}
              className="w-full bg-transparent border-0 px-2 py-2.5 text-[15px] focus:outline-none focus:ring-0 text-text-primary resize-none placeholder-text-tertiary leading-relaxed max-h-[250px]"
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
              className={`p-2.5 mb-0.5 shrink-0 rounded-xl flex items-center justify-center transition-all duration-200 shadow-md ${
                (isTyping || isRetrievingContext || isComparing)
                ? "bg-surface-base text-text-primary border border-border-light hover:bg-surface-hover animate-pulse" 
                : (input.trim() || attachment) 
                  ? "bg-accent-iris text-white hover:bg-indigo-600 border border-transparent" 
                  : "bg-surface-base text-text-tertiary border border-border-light cursor-not-allowed"
              }`}
            >
              {(isTyping || isRetrievingContext || isComparing) ? <Square fill="currentColor" size={16} /> : <ArrowUp size={18} strokeWidth={2.5} />}
            </button>
            </div>
          </motion.form>
          <div className="text-center mt-3 text-[12px] text-text-tertiary">
            Multimodal Research Engine • Optimized for {isResearchMode ? 'Accuracy' : 'Creativity'}
          </div>
        </div>
      </div>
    </>
  );
}
