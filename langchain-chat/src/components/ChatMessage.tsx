import React from 'react';
import { motion } from 'framer-motion';
import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <motion.div
      className={`message ${message.sender}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        type: 'spring',
        stiffness: 100,
        damping: 10,
      }}
      exit={{ opacity: 0, x: message.sender === 'user' ? 50 : -50 }}
    >
      <div className="message-content">{message.text}</div>
      <div className="message-time">
        {new Date(message.timestamp).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </div>
    </motion.div>
  );
}; 