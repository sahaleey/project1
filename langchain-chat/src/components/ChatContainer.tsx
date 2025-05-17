import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '../store/chatStore';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ErrorBoundary, FallbackProps } from 'react-error-boundary';
import { Message } from '../types';

const ErrorFallback: React.FC<FallbackProps> = ({ error, resetErrorBoundary }) => (
  <div className="error-container">
    <h3>Something went wrong:</h3>
    <pre>{error.message}</pre>
    <button onClick={resetErrorBoundary}>Try again</button>
  </div>
);

const WelcomeMessage: React.FC = () => (
  <motion.div
    className="welcome-message"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ delay: 0.5 }}
  >
    <h3>Welcome to Abha Chat!</h3>
    <p>Ask me anything about Abha Student Community Union and I'll help you out.</p>
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
);

export const ChatContainer: React.FC = () => {
  const { messages, isLoading, error, sendMessage, addMessage } = useChatStore();
  const messageEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    addMessage({
      sender: 'user',
      text,
    });
    await sendMessage(text);
  };

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => window.location.reload()}
    >
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
              Abha Chat
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
              <WelcomeMessage />
            ) : (
              <AnimatePresence initial={false} mode="wait">
                {messages.map((message: Message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}
              </AnimatePresence>
            )}

            {error && (
              <motion.div
                className="error-message"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {error}
              </motion.div>
            )}

            <div ref={messageEndRef} />
          </div>

          <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        </div>
      </motion.div>
    </ErrorBoundary>
  );
}; 