import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Copy, ThumbsUp, ThumbsDown, Database, Image as ImageIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import SourcePanel from './SourcePanel';

export default function Message({ role, content, sources, model, isRetrievingContext, imageUrl, isComparison }) {
  const isUser = role === 'user';
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 260, damping: 20 }}
      className={`flex w-full group ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex gap-4 w-full max-w-3xl ${isUser ? 'flex-row-reverse' : ''}`}>
        
        {/* Assistant Avatar */}
        {!isUser && (
          <div className="w-8 h-8 shrink-0 rounded-full flex items-center justify-center border border-border-active mt-1">
             <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-text-primary">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
             </svg>
          </div>
        )}
        
        <div className={`flex flex-col min-w-0 ${isUser ? 'max-w-[75%]' : 'flex-1'}`}>
          
          {/* Skeleton RAG Retrieving Pill */}
          <AnimatePresence>
            {isRetrievingContext && !isUser && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                className="flex items-center gap-2 text-xs text-text-secondary bg-surface-sidebar px-3 py-2 rounded-xl mb-3 w-max"
              >
                <Database size={14} className="animate-pulse text-accent-emerald" />
                <span>Synthesizing knowledge...</span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* IMAGE CONTENT (Multimodal) */}
          {imageUrl && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative mt-2 mb-4 rounded-xl overflow-hidden group/img w-max"
            >
              <img src={imageUrl} alt="AI Generated" className="w-full max-w-sm object-cover aspect-square rounded-xl" />
            </motion.div>
          )}

          {/* TEXT CONTENT */}
          {content && (
            <div className={`prose prose-invert prose-p:leading-relaxed max-w-none text-[15px] ${
              isUser 
                ? 'bg-surface-card text-text-primary px-5 py-3 rounded-3xl' 
                : 'text-text-primary py-1'
            }`}>
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}

          {/* Sources Carousel */}
          {!isUser && sources && sources.length > 0 && (
            <div className="mt-3">
              <SourcePanel sources={sources} />
            </div>
          )}

          {/* Action Row */}
          {!isUser && (content || imageUrl) && !isRetrievingContext && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }} 
              className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <button className="p-1.5 text-text-tertiary hover:text-text-primary hover:bg-surface-hover rounded-md transition-colors"><Copy size={14} /></button>
              <button className="p-1.5 text-text-tertiary hover:text-text-primary hover:bg-surface-hover rounded-md transition-colors"><ThumbsUp size={14} /></button>
              <button className="p-1.5 text-text-tertiary hover:text-text-primary hover:bg-surface-hover rounded-md transition-colors"><ThumbsDown size={14} /></button>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

