import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Sparkles, Copy, ThumbsUp, ThumbsDown, Database, User, Image as ImageIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import SourcePanel from './SourcePanel';

export default function Message({ role, content, sources, model, isRetrievingContext, imageUrl, isComparison }) {
  const isUser = role === 'user';
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 20 }}
      className={`flex gap-4 group w-full ${isUser ? 'justify-end' : ''} ${isComparison ? 'bg-surface-sidebar/30 p-6 rounded-3xl border border-border-light/50' : ''}`}
    >
      {/* AI Avatar */}
      {!isUser && (
        <div className={`w-9 h-9 shrink-0 rounded-xl flex items-center justify-center bg-surface-sidebar border border-border-light shadow-sm text-accent-iris mt-1 group-hover:bg-surface-hover/50 transition-colors ${isComparison ? 'bg-accent-iris text-white' : ''}`}>
          <Sparkles size={18} />
        </div>
      )}
      
      <div className={`flex flex-col min-w-0 ${isUser ? 'max-w-[75%] items-end' : 'flex-1 max-w-[85%]'}`}>
        
        {/* Model Badge */}
        {!isUser && model && !isRetrievingContext && (
          <div className="inline-flex items-center gap-1.5 mb-2.5 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest text-text-tertiary">
            {model} {isComparison && <span className="text-accent-iris ml-2">• Research Mode</span>}
          </div>
        )}

        {/* Skeleton RAG Retrieving Pill */}
        <AnimatePresence>
          {isRetrievingContext && !isUser && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              className="flex items-center gap-2 text-xs text-text-secondary bg-surface-sidebar shadow-md px-4 py-3 rounded-xl border border-border-light mb-3"
            >
              <Database size={14} className="animate-pulse text-accent-iris" />
              <span className="font-medium">Synthesizing knowledge from vector index...</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* IMAGE CONTENT (Multimodal) */}
        {imageUrl && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative mt-2 mb-4 rounded-2xl overflow-hidden border border-border-light shadow-2xl group/img"
          >
            <img src={imageUrl} alt="AI Generated" className="w-full max-w-lg object-cover aspect-square" />
            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/img:opacity-100 transition-opacity flex items-center justify-center">
               <button className="bg-white/20 backdrop-blur-md text-white px-4 py-2 rounded-xl flex items-center gap-2 border border-white/30 hover:bg-white/30 transition-all font-medium">
                 <ImageIcon size={16} />
                 <span>Download HD Research Asset</span>
               </button>
            </div>
          </motion.div>
        )}

        {/* TEXT CONTENT */}
        {content && (
          <div className={`prose prose-invert prose-p:leading-relaxed prose-pre:bg-surface-base prose-pre:border prose-pre:border-border-light max-w-none text-[15px] ${
            isUser 
              ? 'bg-surface-sidebar text-text-primary px-6 py-4 rounded-3xl rounded-tr-md border border-border-light shadow-md' 
              : 'text-text-primary'
          }`}>
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}

        {/* Sources Carousel */}
        {!isUser && sources && sources.length > 0 && (
          <SourcePanel sources={sources} />
        )}

        {/* Action Row */}
        {!isUser && (content || imageUrl) && !isRetrievingContext && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }} 
            className="flex items-center gap-1 mt-4 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <button className="p-1.5 text-text-tertiary hover:text-text-primary hover:bg-surface-sidebar rounded-lg transition-colors border border-transparent hover:border-border-light"><Copy size={16} /></button>
            <button className="p-1.5 text-text-tertiary hover:text-accent-emerald hover:bg-surface-sidebar rounded-lg transition-colors border border-transparent hover:border-border-light"><ThumbsUp size={16} /></button>
            <button className="p-1.5 text-text-tertiary hover:text-red-400 hover:bg-surface-sidebar rounded-lg transition-colors border border-transparent hover:border-border-light"><ThumbsDown size={16} /></button>
          </motion.div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="w-9 h-9 shrink-0 rounded-xl flex items-center justify-center bg-gradient-to-tr from-accent-iris to-indigo-400 shadow-md text-white mt-1">
          <User size={18} />
        </div>
      )}
    </motion.div>
  );
}
