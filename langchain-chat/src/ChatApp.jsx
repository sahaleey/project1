import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiLoader } from 'react-icons/fi';
import { IoMdSend } from 'react-icons/io';

export default function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messageEndRef = useRef(null);
  const inputRef = useRef(null);

  // Enhanced scroll behavior with animation
  const scrollToBottom = () => {
    messageEndRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
    });
  };

  useEffect(scrollToBottom, [messages]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = input.trim();
    setMessages((prev) => [...prev, { sender: 'user', text: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { sender: 'bot', text: data.response }]);
    } catch (error) {
      setMessages((prev) => [...prev, { sender: 'bot', text: 'Error: ' + error.message }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Typing animation for loading state
  const TypingIndicator = () => (
    <motion.div
      className="typing-indicator"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="typing-dots">
        {[...Array(3)].map((_, i) => (
          <motion.span
            key={i}
            animate={{
              y: [0, -5, 0],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              repeat: Infinity,
              duration: 1.2,
              delay: i * 0.2,
            }}
          />
        ))}
      </div>
    </motion.div>
  );

  return (
    <motion.div
      className="chat-app-container"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="chat-app">
        <div className="chat-header">
          <motion.h2
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            ABHA AI
          </motion.h2>
          <motion.div
            className="status-indicator"
            animate={{
              backgroundColor: isLoading ? '#ffc107' : '#4caf50',
              boxShadow: isLoading
                ? '0 0 8px rgba(255, 193, 7, 0.5)'
                : '0 0 8px rgba(76, 175, 80, 0.5)',
            }}
            transition={{ duration: 0.3 }}
          />
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <motion.div
              className="welcome-message"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <h3>Welcome!</h3>
              <p>Ask me anything and I'll do my best to help.</p>
              <div className="welcome-animation">
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{
                      y: [0, -15, 0],
                      opacity: [0.6, 1, 0.6],
                    }}
                    transition={{
                      repeat: Infinity,
                      duration: 2,
                      delay: i * 0.2,
                    }}
                  />
                ))}
              </div>
            </motion.div>
          ) : (
            <AnimatePresence>
              {messages.map((m, i) => (
                <motion.div
                  key={i}
                  className={`message ${m.sender}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    type: 'spring',
                    stiffness: 100,
                    damping: 10,
                    delay: m.sender === 'user' ? 0 : 0.1,
                  }}
                  exit={{ opacity: 0, x: m.sender === 'user' ? 50 : -50 }}
                >
                  <div className="message-content">{m.text}</div>
                  <div className="message-time">
                    {new Date().toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}

          {isLoading && messages.length > 0 && (
            <motion.div
              className="message bot"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <TypingIndicator />
            </motion.div>
          )}

          <div ref={messageEndRef} />
        </div>

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
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            animate={{
              height: input.split('\n').length > 1 ? 'auto' : '50px',
            }}
            transition={{ type: 'spring', stiffness: 300 }}
          />
          <motion.button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            whileHover={!isLoading && input.trim() ? { scale: 1.05 } : {}}
            whileTap={!isLoading && input.trim() ? { scale: 0.95 } : {}}
            animate={{
              backgroundColor: isLoading ? '#555' : input.trim() ? '#4a6bff' : '#555',
              color: isLoading || !input.trim() ? '#aaa' : '#fff',
            }}
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
      </div>

      <style jsx global>{`
        :root {
          --primary: #4a6bff;
          --primary-dark: #3a5bef;
          --user-message: var(--primary);
          --bot-message: #2d3748;
          --background: #121212;
          --surface: #1e1e1e;
          --text-primary: #ffffff;
          --text-secondary: #a0aec0;
          --success: #4caf50;
          --warning: #ffc107;
        }

        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }

        body {
          background-color: var(--background);
          color: var(--text-primary);
          font-family:
            'Inter',
            -apple-system,
            BlinkMacSystemFont,
            'Segoe UI',
            Roboto,
            Oxygen,
            Ubuntu,
            Cantarell,
            sans-serif;
          line-height: 1.6;
        }
      `}</style>

      <style jsx>{`
        .chat-app-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          padding: 2rem;
          background: radial-gradient(circle at top right, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        }

        .chat-app {
          display: flex;
          flex-direction: column;
          width: 100%;
          max-width: 800px;
          height: 90vh;
          background-color: var(--surface);
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
          position: relative;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .chat-header {
          padding: 1.5rem;
          background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
          color: white;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .chat-header h2 {
          font-weight: 600;
          font-size: 1.5rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          position: relative;
        }

        .messages-container {
          flex: 1;
          padding: 1.5rem;
          overflow-y: auto;
          background:
            linear-gradient(rgba(30, 30, 30, 0.9), rgba(30, 30, 30, 0.9)),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
          scrollbar-width: thin;
          scrollbar-color: var(--primary) rgba(255, 255, 255, 0.1);
        }

        .messages-container::-webkit-scrollbar {
          width: 6px;
        }

        .messages-container::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
        }

        .messages-container::-webkit-scrollbar-thumb {
          background-color: var(--primary);
          border-radius: 3px;
        }

        .message {
          max-width: 80%;
          margin-bottom: 1.25rem;
          position: relative;
        }

        .message.user {
          margin-left: auto;
        }

        .message.bot {
          margin-right: auto;
        }

        .message-content {
          padding: 0.75rem 1.25rem;
          border-radius: 18px;
          font-size: 0.95rem;
          line-height: 1.5;
          position: relative;
          word-wrap: break-word;
          white-space: pre-wrap;
        }

        .message.user .message-content {
          background: var(--user-message);
          color: white;
          border-bottom-right-radius: 4px;
        }

        .message.bot .message-content {
          background: var(--bot-message);
          color: var(--text-primary);
          border-bottom-left-radius: 4px;
        }

        .message-time {
          font-size: 0.7rem;
          color: var(--text-secondary);
          margin-top: 0.25rem;
          text-align: right;
          padding-right: 0.5rem;
        }

        .message.user .message-time {
          text-align: right;
        }

        .message.bot .message-time {
          text-align: left;
        }

        .input-container {
          display: flex;
          padding: 1rem;
          background-color: rgba(30, 30, 30, 0.8);
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          gap: 0.75rem;
          align-items: flex-end;
        }

        textarea {
          flex: 1;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 0.75rem 1rem;
          color: var(--text-primary);
          font-family: inherit;
          font-size: 0.95rem;
          resize: none;
          outline: none;
          transition: all 0.3s ease;
          max-height: 150px;
          min-height: 50px;
        }

        textarea:focus {
          border-color: var(--primary);
          box-shadow: 0 0 0 2px rgba(74, 107, 255, 0.2);
        }

        textarea::placeholder {
          color: var(--text-secondary);
        }

        button {
          width: 50px;
          height: 50px;
          border-radius: 12px;
          border: none;
          display: flex;
          justify-content: center;
          align-items: center;
          cursor: pointer;
          font-size: 1.25rem;
          transition: all 0.2s ease;
          background-color: var(--primary);
          color: white;
        }

        button:disabled {
          cursor: not-allowed;
          opacity: 0.7;
        }

        .typing-indicator {
          display: flex;
          padding: 0.75rem 1.25rem;
        }

        .typing-dots {
          display: flex;
          align-items: center;
          height: 24px;
        }

        .typing-dots span {
          width: 8px;
          height: 8px;
          margin: 0 2px;
          background-color: var(--text-secondary);
          border-radius: 50%;
          display: inline-block;
        }

        .welcome-message {
          text-align: center;
          padding: 2rem;
          color: var(--text-secondary);
        }

        .welcome-message h3 {
          color: var(--text-primary);
          margin-bottom: 0.5rem;
          font-size: 1.5rem;
        }

        .welcome-message p {
          margin-bottom: 1.5rem;
        }

        .welcome-animation {
          display: flex;
          justify-content: center;
          gap: 8px;
          height: 40px;
          align-items: flex-end;
        }

        .welcome-animation div {
          width: 8px;
          background: var(--primary);
          border-radius: 4px;
        }

        .welcome-animation div:nth-child(1) {
          height: 20px;
        }

        .welcome-animation div:nth-child(2) {
          height: 30px;
        }

        .welcome-animation div:nth-child(3) {
          height: 40px;
        }

        .welcome-animation div:nth-child(4) {
          height: 30px;
        }

        .welcome-animation div:nth-child(5) {
          height: 20px;
        }
      `}</style>
    </motion.div>
  );
}
