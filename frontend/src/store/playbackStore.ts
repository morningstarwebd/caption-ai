/* Playback Store — video playback state */

import { create } from "zustand";

interface PlaybackState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  playbackRate: number;
  zoom: number; // 25 | 50 | 75 | 100
  quality: "full" | "half" | "quarter";
  showSafeZone: boolean;
  showCaptionOverlay: boolean;

  play: () => void;
  pause: () => void;
  togglePlayPause: () => void;
  stop: () => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setVolume: (vol: number) => void;
  setPlaybackRate: (rate: number) => void;
  setZoom: (zoom: number) => void;
  setQuality: (q: "full" | "half" | "quarter") => void;
  toggleSafeZone: () => void;
  toggleCaptionOverlay: () => void;
  seekBy: (delta: number) => void;
}

export const usePlaybackStore = create<PlaybackState>((set) => ({
  isPlaying: false,
  currentTime: 0,
  duration: 0,
  volume: 1,
  playbackRate: 1,
  zoom: 100,
  quality: "full",
  showSafeZone: false,
  showCaptionOverlay: true,

  play: () => set({ isPlaying: true }),
  pause: () => set({ isPlaying: false }),
  togglePlayPause: () => set((s) => ({ isPlaying: !s.isPlaying })),
  stop: () => set({ isPlaying: false, currentTime: 0 }),
  setCurrentTime: (time) => set({ currentTime: time }),
  setDuration: (duration) => set({ duration }),
  setVolume: (vol) => set({ volume: Math.max(0, Math.min(1, vol)) }),
  setPlaybackRate: (rate) => set({ playbackRate: rate }),
  setZoom: (zoom) => set({ zoom }),
  setQuality: (q) => set({ quality: q }),
  toggleSafeZone: () => set((s) => ({ showSafeZone: !s.showSafeZone })),
  toggleCaptionOverlay: () =>
    set((s) => ({ showCaptionOverlay: !s.showCaptionOverlay })),
  seekBy: (delta) =>
    set((s) => ({
      currentTime: Math.max(0, Math.min(s.duration, s.currentTime + delta)),
    })),
}));
