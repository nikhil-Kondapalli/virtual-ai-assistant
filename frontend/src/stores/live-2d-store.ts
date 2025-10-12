import { create } from "zustand";

export type Live2DModel = {
  id: string;
  name: string;
  path: string;
  isLoaded: boolean;
  isPlaying: boolean;
  currentAnimation?: string;
};

export type Live2DState = {
  model: Live2DModel | null;
  isInitialized: boolean;
  error: string | null;

  setModel: (model: Live2DModel) => void;
  setLoaded: (loaded: boolean) => void;
  setPlaying: (playing: boolean) => void;
  setAnimation: (animation: string) => void;
  setInitialized: (initialized: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
};

export const useLive2DStore = create<Live2DState>(set => ({
  model: null,
  isInitialized: false,
  error: null,

  setModel: model => {
    set({ model });
  },

  setLoaded: loaded => {
    set(state => ({
      model: state.model ? { ...state.model, isLoaded: loaded } : null
    }));
  },

  setPlaying: playing => {
    set(state => ({
      model: state.model ? { ...state.model, isPlaying: playing } : null
    }));
  },

  setAnimation: animation => {
    set(state => ({
      model: state.model
        ? { ...state.model, currentAnimation: animation }
        : null
    }));
  },

  setInitialized: initialized => {
    set({ isInitialized: initialized });
  },

  setError: error => {
    set({ error });
  },

  reset: () => {
    set({
      model: null,
      isInitialized: false,
      error: null
    });
  }
}));
