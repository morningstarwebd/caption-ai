/* Timeline Store — timeline zoom, scroll, tracks */

import { create } from "zustand";
import { TimelineTrack } from "@/lib/types";

interface TimelineState {
  pixelsPerSecond: number;
  scrollLeft: number;
  snapEnabled: boolean;

  tracks: TimelineTrack[];

  setPixelsPerSecond: (pps: number) => void;
  setScrollLeft: (sl: number) => void;
  toggleSnap: () => void;
  zoomIn: () => void;
  zoomOut: () => void;

  addTrack: (track: TimelineTrack) => void;
  removeTrack: (id: string) => void;
  toggleTrackLock: (id: string) => void;
  toggleTrackVisibility: (id: string) => void;
  initDefaultTracks: () => void;
}

const DEFAULT_PPS = 40; // pixels per second
const MIN_PPS = 5;
const MAX_PPS = 200;

export const useTimelineStore = create<TimelineState>((set) => ({
  pixelsPerSecond: DEFAULT_PPS,
  scrollLeft: 0,
  snapEnabled: true,

  tracks: [],

  setPixelsPerSecond: (pps) =>
    set({ pixelsPerSecond: Math.max(MIN_PPS, Math.min(MAX_PPS, pps)) }),

  setScrollLeft: (sl) => set({ scrollLeft: Math.max(0, sl) }),

  toggleSnap: () => set((s) => ({ snapEnabled: !s.snapEnabled })),

  zoomIn: () =>
    set((s) => ({
      pixelsPerSecond: Math.min(MAX_PPS, s.pixelsPerSecond * 1.3),
    })),

  zoomOut: () =>
    set((s) => ({
      pixelsPerSecond: Math.max(MIN_PPS, s.pixelsPerSecond / 1.3),
    })),

  addTrack: (track) =>
    set((s) => ({ tracks: [...s.tracks, track] })),

  removeTrack: (id) =>
    set((s) => ({ tracks: s.tracks.filter((t) => t.id !== id) })),

  toggleTrackLock: (id) =>
    set((s) => ({
      tracks: s.tracks.map((t) =>
        t.id === id ? { ...t, locked: !t.locked } : t
      ),
    })),

  toggleTrackVisibility: (id) =>
    set((s) => ({
      tracks: s.tracks.map((t) =>
        t.id === id ? { ...t, visible: !t.visible } : t
      ),
    })),

  initDefaultTracks: () =>
    set({
      tracks: [
        { id: "v1", type: "video", label: "V1", locked: false, visible: true, height: 48 },
        { id: "a1", type: "audio", label: "A1", locked: false, visible: true, height: 48 },
        { id: "c1", type: "caption", label: "C1", locked: false, visible: true, height: 36 },
      ],
    }),
}));
