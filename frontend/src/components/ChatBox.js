import React, { useEffect, useRef } from 'react';
import Message from './Message';

const ChatBox = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-box glass flex-1 overflow-y-auto p-4 mb-4">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-muted">
          <h2 className="text-2xl font-bold mb-2">Welcome to Multimodal RAG</h2>
          <p>Ask anything or upload an image to get started.</p>
        </div>
      ) : (
        messages.map((msg, index) => (
          <Message key={index} message={msg} />
        ))
      )}
      {isLoading && (
        <div className="message assistant fade-in">
          <div className="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatBox;
