import { useState, useCallback } from 'react';
import { chatApi } from '../services/api';

const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);

  const sendMessage = useCallback(async (content) => {
    setIsLoading(true);
    setError(null);
    
    // Add user message immediately
    const userMessage = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);

    try {
      // Check if it's an image generation request
      if (content.toLowerCase().startsWith('/image ')) {
        const prompt = content.replace('/image ', '');
        const data = await chatApi.generateImage(prompt);
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `Generated image for: ${prompt}`,
          image_url: data.image_url 
        }]);
      } else {
        const data = await chatApi.sendMessage(content, conversationId);
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.answer,
          sources: data.sources
        }]);
        if (data.conversation_id) {
          setConversationId(data.conversation_id);
        }
      }
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  return { messages, sendMessage, isLoading, error };
};

export default useChat;
