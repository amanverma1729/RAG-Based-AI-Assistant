import React, { useState } from 'react';
import ChatBox from '../components/ChatBox';
import InputBox from '../components/InputBox';
import useChat from '../hooks/useChat';

const Home = () => {
  const { messages, sendMessage, isLoading, error } = useChat();

  return (
    <div className="app-container">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
            Multimodal RAG
          </h1>
          <p className="text-text-muted">Research-grade AI Assistant</p>
        </div>
        <div className="status-indicator flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
          <span className="text-xs font-medium text-accent">System Online</span>
        </div>
      </header>

      {error && (
        <div className="mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm">
          {error}
        </div>
      )}

      <ChatBox messages={messages} isLoading={isLoading} />
      <InputBox onSendMessage={sendMessage} isLoading={isLoading} />
      
      <footer className="mt-4 text-center text-xs text-text-muted">
        Powered by OpenAI & PostgreSQL Vector Store
      </footer>
    </div>
  );
};

export default Home;
