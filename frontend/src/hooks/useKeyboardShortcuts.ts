/* useKeyboardShortcuts — Premiere Pro-style keyboard shortcuts */

"use client";

import { useEffect } from "react";
import { usePlaybackStore } from "@/store/playbackStore";
import { useEditorStore } from "@/store/editorStore";
import { useCaptionStore } from "@/store/captionStore";
import { useTimelineStore } from "@/store/timelineStore";

export function useKeyboardShortcuts() {
  const playback = usePlaybackStore;
  const editor = useEditorStore;
  const captions = useCaptionStore;
  const timeline = useTimelineStore;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't fire shortcuts when typing in inputs
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        return;
      }

      const ctrl = e.ctrlKey || e.metaKey;
      const shift = e.shiftKey;

      switch (e.key) {
        // Space — Play/Pause
        case " ":
          e.preventDefault();
          playback.getState().togglePlayPause();
          break;

        // V — Selection tool
        case "v":
        case "V":
          if (!ctrl) editor.getState().setActiveTool("selection");
          break;

        // C — Razor tool
        case "c":
        case "C":
          if (!ctrl) editor.getState().setActiveTool("razor");
          break;

        // H — Hand tool
        case "h":
        case "H":
          if (!ctrl) editor.getState().setActiveTool("hand");
          break;

        // Z — Zoom tool
        case "z":
        case "Z":
          if (!ctrl && !shift) editor.getState().setActiveTool("zoom");
          break;

        // Ctrl+Z — Undo
        case "z":
          if (ctrl && !shift) {
            e.preventDefault();
            captions.getState().undo();
          }
          break;

        // Ctrl+Shift+Z — Redo
        case "Z":
          if (ctrl && shift) {
            e.preventDefault();
            captions.getState().redo();
          }
          break;

        // Arrow keys — frame navigation
        case "ArrowRight":
          e.preventDefault();
          playback.getState().seekBy(shift ? 5 / 30 : 1 / 30);
          break;

        case "ArrowLeft":
          e.preventDefault();
          playback.getState().seekBy(shift ? -5 / 30 : -1 / 30);
          break;

        // Delete
        case "Delete":
        case "Backspace":
          captions.getState().deleteSelected();
          break;

        // Ctrl+A — Select all captions
        case "a":
        case "A":
          if (ctrl) {
            e.preventDefault();
            captions.getState().selectAll();
          }
          break;

        // + / - — Timeline zoom
        case "+":
        case "=":
          timeline.getState().zoomIn();
          break;
        case "-":
        case "_":
          timeline.getState().zoomOut();
          break;

        // G — Generate captions
        case "g":
        case "G":
          if (!ctrl) {
            // Trigger caption generation via button click simulation
            document.getElementById("generate-captions-btn")?.click();
          }
          break;

        // Ctrl+M — Export
        case "m":
        case "M":
          if (ctrl) {
            e.preventDefault();
            editor.getState().setShowExportModal(true);
          }
          break;

        // Ctrl+S — Save project
        case "s":
        case "S":
          if (ctrl) {
            e.preventDefault();
            // TODO: project save
          }
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);
}
