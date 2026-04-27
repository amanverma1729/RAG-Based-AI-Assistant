import React from 'react';

const Message = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message ${isUser ? 'user' : 'assistant'} fade-in mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] p-4 rounded-2xl ${isUser ? 'bg-primary text-white rounded-tr-none' : 'bg-card text-text-main border border-border rounded-tl-none'}`}>
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-border/50 text-xs text-text-muted">
            <span className="font-semibold">Sources:</span>
            <ul className="list-disc ml-4 mt-1">
              {message.sources.map((src, i) => (
                <li key={i}>{src.title || src.filename}</li>
              ))}
            </ul>
          </div>
        )}
        {message.image_url && (
          <div className="mt-3 rounded-lg overflow-hidden border border-border">
            <img src={message.image_url} alt="Generated" className="w-full h-auto" />
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
