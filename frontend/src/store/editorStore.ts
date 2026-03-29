/* Editor Store — global editor state */

import { create } from "zustand";
import { Language, CaptionTheme, ToolMode, MediaFile } from "@/lib/types";

interface EditorState {
  // Tool
  activeTool: ToolMode;
  setActiveTool: (tool: ToolMode) => void;

  // Media
  mediaFiles: MediaFile[];
  activeMediaId: string | null;
  addMedia: (file: MediaFile) => void;
  removeMedia: (id: string) => void;
  setActiveMedia: (id: string | null) => void;

  // Settings
  language: Language;
  setLanguage: (lang: Language) => void;
  theme: CaptionTheme;
  setTheme: (theme: CaptionTheme) => void;

  // Pipeline
  jobId: string | null;
  setJobId: (id: string | null) => void;
  pipelineStatus: string;
  pipelinePercent: number;
  setPipelineProgress: (status: string, percent: number) => void;

  // Panels
  mediaPanelTab: "project" | "effects" | "history";
  setMediaPanelTab: (tab: "project" | "effects" | "history") => void;

  // Export
  showExportModal: boolean;
  setShowExportModal: (show: boolean) => void;
}

export const useEditorStore = create<EditorState>((set) => ({
  activeTool: "selection",
  setActiveTool: (tool) => set({ activeTool: tool }),

  mediaFiles: [],
  activeMediaId: null,
  addMedia: (file) =>
    set((state) => ({
      mediaFiles: [...state.mediaFiles, file],
      activeMediaId: state.activeMediaId || file.id,
    })),
  removeMedia: (id) =>
    set((state) => ({
      mediaFiles: state.mediaFiles.filter((f) => f.id !== id),
      activeMediaId: state.activeMediaId === id ? null : state.activeMediaId,
    })),
  setActiveMedia: (id) => set({ activeMediaId: id }),

  language: "auto",
  setLanguage: (lang) => set({ language: lang }),
  theme: "viral_shorts",
  setTheme: (theme) => set({ theme }),

  jobId: null,
  setJobId: (id) => set({ jobId: id }),
  pipelineStatus: "",
  pipelinePercent: 0,
  setPipelineProgress: (status, percent) =>
    set({ pipelineStatus: status, pipelinePercent: percent }),

  mediaPanelTab: "project",
  setMediaPanelTab: (tab) => set({ mediaPanelTab: tab }),

  showExportModal: false,
  setShowExportModal: (show) => set({ showExportModal: show }),
}));
