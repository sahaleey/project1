# Abha Chat Frontend

A modern, responsive chat interface for the Abha Student Community Union chatbot.

## Features

- 🎨 Modern, responsive design with dark theme
- ✨ Smooth animations and transitions
- 💾 Persistent chat history
- ⚡ Real-time chat with AI
- ♿ Accessibility features
- 🛡️ Error handling and recovery
- 📱 Mobile-friendly interface

## Tech Stack

- React 18
- TypeScript
- Framer Motion for animations
- Zustand for state management
- Axios for API calls
- React Error Boundary for error handling

## Prerequisites

- Node.js 16 or higher
- npm 7 or higher
- Backend server running on http://localhost:8000

## Quick Start

1. Run the setup script:
   ```bash
   setup.bat
   ```

   This will:
   - Install all dependencies
   - Set up TypeScript
   - Create environment files
   - Start the development server

2. Open http://localhost:3000 in your browser

## Manual Setup

If you prefer to set up manually:

1. Install dependencies:
   ```bash
   npm install
   ```

2. Install TypeScript dependencies:
   ```bash
   npm install --save-dev typescript @types/node @types/react @types/react-dom @types/jest @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-config-prettier prettier
   ```

3. Create `.env` file:
   ```
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_MESSAGES_STORAGE_KEY=chat_messages
   ```

4. Start development server:
   ```bash
   npm start
   ```

## Development

- `npm start` - Start development server
- `npm run build` - Create production build
- `npm test` - Run tests
- `npm run lint` - Run linter
- `npm run format` - Format code

## Project Structure

```
src/
  ├── components/          # React components
  │   ├── ChatContainer.tsx
  │   ├── ChatInput.tsx
  │   └── ChatMessage.tsx
  ├── store/              # State management
  │   └── chatStore.ts
  ├── styles/             # CSS styles
  │   └── App.css
  ├── types/              # TypeScript types
  │   └── index.ts
  └── App.tsx             # Root component
```

## Environment Variables

- `REACT_APP_API_URL` - Backend API URL
- `REACT_APP_MESSAGES_STORAGE_KEY` - Local storage key for messages

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
