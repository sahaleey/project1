import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { persist } from 'zustand/middleware/persist';

import axios from 'axios';

import type { ChatState, Message, ChatResponse } from '../types';
import type { StateCreator } from 'zustand';

const STORAGE_KEY = 'chat-store';
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface ChatStore extends ChatState {
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
}

type State = {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
};

type Actions = {
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
};

type Store = State & Actions;

const initialState: State = {
  messages: [],
  isLoading: false,
  error: null,
};

const storeCreator: StateCreator<Store> = (set, get) => ({
  ...initialState,

  addMessage: (message): void => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      timestamp: new Date().toISOString(),
      ...message,
    };

    set((state) => ({
      messages: [...state.messages, newMessage],
    }));
  },

  sendMessage: async (text): Promise<void> => {
    set({ isLoading: true, error: null });

    try {
      const response = await axios.post<ChatResponse>(
        `${API_URL}/chat`,
        { message: text },
        { headers: { 'Content-Type': 'application/json' } }
      );

      const botMessage: Message = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        sender: 'bot',
        text: response.data.response,
        timestamp: response.data.timestamp || new Date().toISOString(),
      };

      set((state) => ({
        isLoading: false,
        messages: [...state.messages, botMessage],
      }));
    } catch (err: unknown) {
      let errorMessage = 'An error occurred while sending the message';

      if ((err as any)?.isAxiosError) {
        errorMessage = (err as any).message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      set({ isLoading: false, error: errorMessage });
    }
  },

  clearMessages: (): void => {
    set({ messages: [], error: null });
  },
});

const useChatStore = create<Store>()(
  devtools(
    persist(storeCreator, {
      name: STORAGE_KEY,
    })
  )
);

export { useChatStore };
export type { ChatStore, State, Actions, Store };
