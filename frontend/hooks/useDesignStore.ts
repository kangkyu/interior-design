'use client';

import { create } from 'zustand';
import type { Message, DesignVersion, RoomAnalysis } from '@/types';

interface DesignState {
  // Project data
  projectId: string | null;
  projectName: string;

  // Images
  originalImageUrl: string | null;
  currentImageUrl: string | null;
  currentVersion: number;

  // Room analysis
  roomAnalysis: RoomAnalysis | null;

  // Chat
  messages: Message[];
  isLoading: boolean;

  // Versions
  versions: DesignVersion[];

  // UI state
  compareMode: boolean;
  selectedVersion: number | null;

  // Actions
  setProject: (projectId: string, projectName: string) => void;
  setOriginalImage: (url: string) => void;
  setCurrentImage: (url: string, version: number) => void;
  setRoomAnalysis: (analysis: RoomAnalysis) => void;
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
  setLoading: (loading: boolean) => void;
  setVersions: (versions: DesignVersion[]) => void;
  addVersion: (version: DesignVersion) => void;
  toggleCompareMode: () => void;
  selectVersion: (version: number | null) => void;
  reset: () => void;
}

const initialState = {
  projectId: null,
  projectName: '',
  originalImageUrl: null,
  currentImageUrl: null,
  currentVersion: 0,
  roomAnalysis: null,
  messages: [],
  isLoading: false,
  versions: [],
  compareMode: false,
  selectedVersion: null,
};

export const useDesignStore = create<DesignState>((set) => ({
  ...initialState,

  setProject: (projectId, projectName) =>
    set({ projectId, projectName }),

  setOriginalImage: (url) =>
    set({ originalImageUrl: url, currentImageUrl: url }),

  setCurrentImage: (url, version) =>
    set({ currentImageUrl: url, currentVersion: version }),

  setRoomAnalysis: (analysis) =>
    set({ roomAnalysis: analysis }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setMessages: (messages) =>
    set({ messages }),

  setLoading: (loading) =>
    set({ isLoading: loading }),

  setVersions: (versions) =>
    set({ versions }),

  addVersion: (version) =>
    set((state) => ({
      versions: [...state.versions, version],
    })),

  toggleCompareMode: () =>
    set((state) => ({ compareMode: !state.compareMode })),

  selectVersion: (version) =>
    set({ selectedVersion: version }),

  reset: () =>
    set(initialState),
}));
