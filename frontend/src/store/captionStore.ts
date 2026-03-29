/* Caption Store — caption list state and operations */

import { create } from "zustand";
import { Caption, CaptionTheme } from "@/lib/types";
import { generateCaptionId } from "@/lib/captionUtils";

interface CaptionState {
  captions: Caption[];
  selectedIds: Set<string>;
  editingId: string | null;

  // CRUD
  setCaptions: (captions: Caption[]) => void;
  addCaption: (caption: Omit<Caption, "id">) => void;
  updateCaption: (id: string, updates: Partial<Caption>) => void;
  deleteCaption: (id: string) => void;
  deleteSelected: () => void;
  clearAll: () => void;

  // Selection
  selectCaption: (id: string, multi?: boolean) => void;
  selectAll: () => void;
  deselectAll: () => void;
  setEditingId: (id: string | null) => void;

  // Operations
  splitCaption: (id: string, splitTime: number) => void;
  mergeCaptions: (ids: string[]) => void;
  setThemeForAll: (theme: CaptionTheme) => void;

  // Undo/Redo
  history: Caption[][];
  historyIndex: number;
  pushHistory: () => void;
  undo: () => void;
  redo: () => void;

  // Get caption at time
  getCaptionAtTime: (time: number) => Caption | undefined;
}

export const useCaptionStore = create<CaptionState>((set, get) => ({
  captions: [],
  selectedIds: new Set(),
  editingId: null,
  history: [],
  historyIndex: -1,

  setCaptions: (captions) => {
    get().pushHistory();
    set({ captions });
  },

  addCaption: (caption) => {
    get().pushHistory();
    const newCaption: Caption = { ...caption, id: generateCaptionId() };
    set((s) => ({ captions: [...s.captions, newCaption] }));
  },

  updateCaption: (id, updates) => {
    get().pushHistory();
    set((s) => ({
      captions: s.captions.map((c) => (c.id === id ? { ...c, ...updates } : c)),
    }));
  },

  deleteCaption: (id) => {
    get().pushHistory();
    set((s) => ({
      captions: s.captions.filter((c) => c.id !== id),
      selectedIds: new Set(Array.from(s.selectedIds).filter((sid) => sid !== id)),
    }));
  },

  deleteSelected: () => {
    const { selectedIds } = get();
    if (selectedIds.size === 0) return;
    get().pushHistory();
    set((s) => ({
      captions: s.captions.filter((c) => !selectedIds.has(c.id)),
      selectedIds: new Set(),
    }));
  },

  clearAll: () => {
    get().pushHistory();
    set({ captions: [], selectedIds: new Set(), editingId: null });
  },

  selectCaption: (id, multi = false) => {
    set((s) => {
      const newSet = new Set(multi ? s.selectedIds : []);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return { selectedIds: newSet };
    });
  },

  selectAll: () =>
    set((s) => ({ selectedIds: new Set(s.captions.map((c) => c.id)) })),

  deselectAll: () => set({ selectedIds: new Set() }),

  setEditingId: (id) => set({ editingId: id }),

  splitCaption: (id, splitTime) => {
    const caption = get().captions.find((c) => c.id === id);
    if (!caption || splitTime <= caption.start || splitTime >= caption.end)
      return;

    get().pushHistory();
    const words = caption.text.split(" ");
    const ratio = (splitTime - caption.start) / (caption.end - caption.start);
    const splitIndex = Math.max(1, Math.round(words.length * ratio));

    const text1 = words.slice(0, splitIndex).join(" ");
    const text2 = words.slice(splitIndex).join(" ");

    set((s) => ({
      captions: s.captions.flatMap((c) =>
        c.id === id
          ? [
              { ...c, end: splitTime, text: text1 },
              {
                ...c,
                id: generateCaptionId(),
                start: splitTime,
                text: text2,
              },
            ]
          : [c]
      ),
    }));
  },

  mergeCaptions: (ids) => {
    if (ids.length < 2) return;
    get().pushHistory();
    const toMerge = get()
      .captions.filter((c) => ids.includes(c.id))
      .sort((a, b) => a.start - b.start);

    if (toMerge.length < 2) return;

    const merged: Caption = {
      id: toMerge[0].id,
      start: toMerge[0].start,
      end: toMerge[toMerge.length - 1].end,
      text: toMerge.map((c) => c.text).join(" "),
      lang: toMerge[0].lang,
      theme: toMerge[0].theme,
    };

    const mergeIds = new Set(ids.slice(1));
    set((s) => ({
      captions: s.captions
        .filter((c) => !mergeIds.has(c.id))
        .map((c) => (c.id === merged.id ? merged : c)),
      selectedIds: new Set(),
    }));
  },

  setThemeForAll: (theme) => {
    get().pushHistory();
    set((s) => ({
      captions: s.captions.map((c) => ({ ...c, theme })),
    }));
  },

  pushHistory: () =>
    set((s) => {
      const newHistory = s.history.slice(0, s.historyIndex + 1);
      newHistory.push([...s.captions]);
      // Keep max 50 history entries
      if (newHistory.length > 50) newHistory.shift();
      return { history: newHistory, historyIndex: newHistory.length - 1 };
    }),

  undo: () =>
    set((s) => {
      if (s.historyIndex < 0) return s;
      const captions = s.history[s.historyIndex];
      return {
        captions: captions || s.captions,
        historyIndex: s.historyIndex - 1,
      };
    }),

  redo: () =>
    set((s) => {
      if (s.historyIndex >= s.history.length - 1) return s;
      const captions = s.history[s.historyIndex + 1];
      return {
        captions: captions || s.captions,
        historyIndex: s.historyIndex + 1,
      };
    }),

  getCaptionAtTime: (time) =>
    get().captions.find((c) => time >= c.start && time <= c.end),
}));
