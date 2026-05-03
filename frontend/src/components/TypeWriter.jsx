import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

export default function TypeWriter({ content, onComplete }) {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    let index = 0;
    setDisplayedText('');
    
    const intervalId = setInterval(() => {
      setDisplayedText(prev => {
        const nextChar = content.charAt(index);
        index++;
        if (index >= content.length) {
          clearInterval(intervalId);
          if (onComplete) onComplete();
          return content;
        }
        return prev + nextChar;
      });
    }, 15);

    return () => clearInterval(intervalId);
  }, [content, onComplete]);

  return <ReactMarkdown>{displayedText}</ReactMarkdown>;
}
