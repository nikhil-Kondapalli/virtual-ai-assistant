import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
};

export type ChatSession = {
  id: string;
  persona: string;
  messages: ChatMessage[];
  isConnected: boolean;
  isTyping: boolean;
};

type ChatState = {
  session: ChatSession | null;
  currentMessage: string;
  isConnected: boolean;

  setSession: (session: ChatSession) => void;
  addMessage: (message: Omit<ChatMessage, "id" | "timestamp">) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  setCurrentMessage: (message: string) => void;
  setConnected: (connected: boolean) => void;
  setTyping: (typing: boolean) => void;
  clearMessages: () => void;
};

export const useChatStore = create<ChatState>()(
  immer(set => ({
    session: null,
    currentMessage: "",
    isConnected: false,

    setSession: session => {
      set(state => {
        state.session = session;
      });
    },

    addMessage: message => {
      set(state => {
        if (state.session) {
          const newMessage: ChatMessage = {
            ...message,
            id: Date.now().toString(),
            timestamp: new Date()
          };
          state.session.messages.push(newMessage);
        }
      });
    },

    updateMessage: (id, updates) => {
      set(state => {
        if (state.session) {
          const message = state.session.messages.find(m => m.id === id);
          if (message) {
            Object.assign(message, updates);
          }
        }
      });
    },

    setCurrentMessage: message => {
      set(state => {
        state.currentMessage = message;
      });
    },

    setConnected: connected => {
      set(state => {
        state.isConnected = connected;
        if (state.session) {
          state.session.isConnected = connected;
        }
      });
    },

    setTyping: typing => {
      set(state => {
        if (state.session) {
          state.session.isTyping = typing;
        }
      });
    },

    clearMessages: () => {
      set(state => {
        if (state.session) {
          state.session.messages = [];
        }
      });
    }
  }))
);
