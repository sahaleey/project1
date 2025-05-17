import React, { useRef, useState, KeyboardEvent, ChangeEvent } from 'react'; 
import { motion } from 'framer-motion';
import { FiLoader } from 'react-icons/fi';
import { IoMdSend } from 'react-icons/io';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  return (
    <motion.div
      className="input-container"
      layout
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <motion.textarea
        ref={inputRef}
        rows={1}
        placeholder="Type your message..."
        value={input}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        animate={{
          height: input.split('\n').length > 1 ? 'auto' : '50px',
        }}
        transition={{ type: 'spring', stiffness: 300 }}
        aria-label="Chat input"
      />
      <motion.button
        onClick={handleSend}
        disabled={isLoading || !input.trim()}
        whileHover={!isLoading && input.trim() ? { scale: 1.05 } : {}}
        whileTap={!isLoading && input.trim() ? { scale: 0.95 } : {}}
        animate={{
          backgroundColor: isLoading
            ? '#555'
            : input.trim()
            ? '#4a6bff'
            : '#555',
          color: isLoading || !input.trim() ? '#aaa' : '#fff',
        }}
        aria-label={isLoading ? 'Sending message...' : 'Send message'}
      >
        {isLoading ? (
          <motion.span
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          >
            <FiLoader />
          </motion.span>
        ) : (
          <IoMdSend />
        )}
      </motion.button>
    </motion.div>
  );
}; 