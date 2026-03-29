/* CaptionEditorPanel — Right panel for caption list, generation, editing */

"use client";

import React, { useState, useCallback } from "react";
import {
  Languages,
  Wand2,
  Plus,
  Trash2,
  Scissors,
  Palette,
} from "lucide-react";
import { useEditorStore } from "@/store/editorStore";
import { useCaptionStore } from "@/store/captionStore";
import { usePlaybackStore } from "@/store/playbackStore";
import { useCaptionExport } from "@/hooks/useCaptionExport";
import { useWebSocket } from "@/hooks/useWebSocket";
import { uploadVideo, getJob } from "@/lib/api";
import { segmentsToCapptions, formatTime, parseTime } from "@/lib/captionUtils";
import { Language, CaptionTheme, CAPTION_THEMES } from "@/lib/types";

const LANGUAGES: { value: Language; label: string }[] = [
  { value: "auto", label: "Auto Detect" },
  { value: "english", label: "English" },
  { value: "hindi", label: "Hindi" },
  { value: "hinglish", label: "Hinglish" },
  { value: "bengali", label: "Bengali" },
];

export default function CaptionEditorPanel() {
  const { language, setLanguage, mediaFiles, activeMediaId, pipelineStatus, pipelinePercent, setJobId, setPipelineProgress } =
    useEditorStore();
  const { captions, selectedIds, editingId, selectCaption, setEditingId, updateCaption, deleteCaption, deleteSelected, addCaption, splitCaption, setCaptions } =
    useCaptionStore();
  const { currentTime } = usePlaybackStore();
  const { exportSRT, exportASS } = useCaptionExport();
  const [isGenerating, setIsGenerating] = useState(false);
  const [stylePickerForId, setStylePickerForId] = useState<string | null>(null);
  const [editingTimeId, setEditingTimeId] = useState<string | null>(null);
  const [editingTimeField, setEditingTimeField] = useState<"start" | "end">("start");

  useWebSocket();

  const activeMedia = mediaFiles.find((f) => f.id === activeMediaId);

  const handleGenerate = useCallback(async () => {
    if (!activeMedia || isGenerating) return;

    setIsGenerating(true);
    setPipelineProgress("Uploading...", 5);

    try {
      const langMap: Record<string, string> = {
        auto: "auto",
        english: "en",
        hindi: "hi",
        hinglish: "hinglish",
        bengali: "bn",
      };

      const result = await uploadVideo(activeMedia.file, langMap[language] || "auto");
      setJobId(result.job_id);

      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const job = await getJob(result.job_id);
          if (job.status === "completed") {
            clearInterval(pollInterval);
            setPipelineProgress("Done", 100);

            if (job.segments) {
              const newCaptions = segmentsToCapptions(
                job.segments,
                language,
                useEditorStore.getState().theme
              );
              setCaptions(newCaptions);
            }
            setIsGenerating(false);
          } else if (job.status === "failed") {
            clearInterval(pollInterval);
            setPipelineProgress("Failed", -1);
            setIsGenerating(false);
          }
        } catch {
          // continue polling
        }
      }, 2000);
    } catch {
      setPipelineProgress("Error", -1);
      setIsGenerating(false);
    }
  }, [activeMedia, isGenerating, language, setJobId, setPipelineProgress, setCaptions]);

  const handleAddCaption = useCallback(() => {
    addCaption({
      start: currentTime,
      end: currentTime + 3,
      text: "New caption",
      lang: language === "auto" ? "english" : language,
      theme: useEditorStore.getState().theme,
    });
  }, [currentTime, addCaption, language]);

  const handleSplit = useCallback(
    (id: string) => {
      splitCaption(id, currentTime);
    },
    [currentTime, splitCaption]
  );

  // ── Inline time editing ──
  const handleTimeClick = useCallback((captionId: string, field: "start" | "end", e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingTimeId(captionId);
    setEditingTimeField(field);
  }, []);

  const handleTimeBlur = useCallback((captionId: string, field: "start" | "end", value: string) => {
    const parsed = parseTime(value);
    if (parsed !== null) {
      updateCaption(captionId, { [field]: parsed });
    }
    setEditingTimeId(null);
  }, [updateCaption]);

  const handleTimeKeyDown = useCallback((captionId: string, field: "start" | "end", e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      const parsed = parseTime(e.currentTarget.value);
      if (parsed !== null) {
        updateCaption(captionId, { [field]: parsed });
      }
      setEditingTimeId(null);
    }
    if (e.key === "Escape") {
      setEditingTimeId(null);
    }
  }, [updateCaption]);

  const sortedCaptions = [...captions].sort((a, b) => a.start - b.start);

  const THEME_NAMES: { id: CaptionTheme; label: string }[] = [
    { id: "minimal", label: "Minimal" },
    { id: "viral_shorts", label: "Viral" },
    { id: "cinematic", label: "Cinema" },
    { id: "kalakar_fire", label: "Fire" },
    { id: "karaoke_neon", label: "Neon" },
    { id: "dramatic", label: "Drama" },
    { id: "glassmorphism", label: "Glass" },
    { id: "retro_vhs", label: "VHS" },
    { id: "neon_glow", label: "Glow" },
    { id: "typewriter", label: "Type" },
    { id: "comic_pop", label: "Comic" },
    { id: "elegant_serif", label: "Serif" },
    { id: "gradient_wave", label: "Gradient" },
    { id: "outline_bold", label: "Outline" },
    { id: "shadow_3d", label: "3D" },
    { id: "highlight_box", label: "Highlight" },
  ];

  const handleApplyThemeToCaption = useCallback(
    (captionId: string, newTheme: CaptionTheme) => {
      updateCaption(captionId, { theme: newTheme, style: CAPTION_THEMES[newTheme] });
      setStylePickerForId(null);
    },
    [updateCaption]
  );

  const handleApplyThemeToAll = useCallback(
    (newTheme: CaptionTheme) => {
      captions.forEach((c) => {
        updateCaption(c.id, { theme: newTheme, style: CAPTION_THEMES[newTheme] });
      });
    },
    [captions, updateCaption]
  );

  return (
    <div className="panel flex flex-col h-full">
      {/* Header */}
      <div className="panel-header">
        <span>Caption Editor</span>
      </div>

      {/* Controls */}
      <div className="p-2 space-y-2 shrink-0" style={{ borderBottom: "1px solid var(--border)" }}>
        {/* Language selector */}
        <div className="flex items-center gap-2">
          <Languages size={14} style={{ color: "var(--text-muted)" }} />
          <select
            className="flex-1 text-xs px-2 py-1 rounded border-0 outline-none cursor-pointer"
            style={{ background: "var(--bg-panel-dark)", color: "var(--text-primary)" }}
            value={language}
            onChange={(e) => setLanguage(e.target.value as Language)}
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        {/* Generate button */}
        <button
          id="generate-captions-btn"
          className="btn-primary w-full flex items-center justify-center gap-2"
          onClick={handleGenerate}
          disabled={!activeMedia || isGenerating}
        >
          <Wand2 size={14} />
          {isGenerating ? "Generating..." : "Generate Captions"}
        </button>

        {/* Progress bar */}
        {pipelinePercent > 0 && pipelinePercent < 100 && (
          <div className="space-y-1">
            <div className="flex justify-between text-[10px]" style={{ color: "var(--text-muted)" }}>
              <span>{pipelineStatus}</span>
              <span>{pipelinePercent}%</span>
            </div>
            <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--bg-panel-dark)" }}>
              <div
                className="h-full rounded-full transition-all duration-300"
                style={{
                  width: `${pipelinePercent}%`,
                  background: "var(--accent)",
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Caption list */}
      <div className="flex-1 overflow-y-auto p-1">
        {sortedCaptions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              No captions yet.
              <br />
              Generate or add manually.
            </p>
          </div>
        ) : (
          sortedCaptions.map((caption) => (
            <div
              key={caption.id}
              className="p-2 mb-1 rounded cursor-pointer transition-colors group"
              style={{
                background: selectedIds.has(caption.id)
                  ? "rgba(77, 159, 255, 0.15)"
                  : "var(--bg-panel-dark)",
                border: selectedIds.has(caption.id)
                  ? "1px solid var(--accent)"
                  : "1px solid transparent",
              }}
              onClick={() => selectCaption(caption.id)}
            >
              {/* Timestamp — clickable for inline edit */}
              <div className="flex items-center gap-1 mb-1">
                {editingTimeId === caption.id && editingTimeField === "start" ? (
                  <input
                    className="font-mono text-[10px] w-16 px-1 py-0 rounded border-0 outline-none"
                    style={{ background: "var(--bg-app)", color: "var(--accent)" }}
                    defaultValue={formatTime(caption.start)}
                    autoFocus
                    onClick={(e) => e.stopPropagation()}
                    onBlur={(e) => handleTimeBlur(caption.id, "start", e.target.value)}
                    onKeyDown={(e) => handleTimeKeyDown(caption.id, "start", e)}
                  />
                ) : (
                  <span
                    className="font-mono text-[10px] cursor-text hover:underline"
                    style={{ color: "var(--accent)" }}
                    onClick={(e) => handleTimeClick(caption.id, "start", e)}
                    title="Click to edit start time"
                  >
                    {formatTime(caption.start)}
                  </span>
                )}
                <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                  →
                </span>
                {editingTimeId === caption.id && editingTimeField === "end" ? (
                  <input
                    className="font-mono text-[10px] w-16 px-1 py-0 rounded border-0 outline-none"
                    style={{ background: "var(--bg-app)", color: "var(--accent)" }}
                    defaultValue={formatTime(caption.end)}
                    autoFocus
                    onClick={(e) => e.stopPropagation()}
                    onBlur={(e) => handleTimeBlur(caption.id, "end", e.target.value)}
                    onKeyDown={(e) => handleTimeKeyDown(caption.id, "end", e)}
                  />
                ) : (
                  <span
                    className="font-mono text-[10px] cursor-text hover:underline"
                    style={{ color: "var(--accent)" }}
                    onClick={(e) => handleTimeClick(caption.id, "end", e)}
                    title="Click to edit end time"
                  >
                    {formatTime(caption.end)}
                  </span>
                )}
                <span
                  className="text-[8px] px-1 py-0.5 rounded ml-auto uppercase"
                  style={{
                    background:
                      caption.lang === "english"
                        ? "var(--caption-en)"
                        : caption.lang === "hindi"
                        ? "var(--caption-hi)"
                        : caption.lang === "hinglish"
                        ? "var(--caption-hing)"
                        : "var(--caption-bn)",
                    color: "var(--text-primary)",
                  }}
                >
                  {caption.lang}
                </span>
              </div>

              {/* Text */}
              {editingId === caption.id ? (
                <input
                  className="w-full text-xs px-1 py-0.5 rounded border-0 outline-none"
                  style={{
                    background: "var(--bg-app)",
                    color: "var(--text-primary)",
                  }}
                  defaultValue={caption.text}
                  autoFocus
                  onBlur={(e) => {
                    updateCaption(caption.id, { text: e.target.value });
                    setEditingId(null);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      updateCaption(caption.id, {
                        text: (e.target as HTMLInputElement).value,
                      });
                      setEditingId(null);
                    }
                    if (e.key === "Escape") setEditingId(null);
                  }}
                />
              ) : (
                <div
                  className="text-xs leading-relaxed"
                  style={{ color: "var(--text-primary)" }}
                  onDoubleClick={() => setEditingId(caption.id)}
                >
                  {caption.text}
                </div>
              )}

              {/* Actions (visible on hover) */}
              <div className="flex gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  className="p-0.5 rounded hover:bg-white/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingId(caption.id);
                  }}
                  title="Edit"
                >
                  <span className="text-[9px]" style={{ color: "var(--text-muted)" }}>
                    Edit
                  </span>
                </button>
                <button
                  className="p-0.5 rounded hover:bg-white/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    setStylePickerForId(stylePickerForId === caption.id ? null : caption.id);
                  }}
                  title="Change style"
                >
                  <Palette size={10} style={{ color: "var(--text-muted)" }} />
                </button>
                <button
                  className="p-0.5 rounded hover:bg-white/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSplit(caption.id);
                  }}
                  title="Split at playhead"
                >
                  <Scissors size={10} style={{ color: "var(--text-muted)" }} />
                </button>
                <button
                  className="p-0.5 rounded hover:bg-white/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteCaption(caption.id);
                  }}
                  title="Delete"
                >
                  <Trash2 size={10} style={{ color: "var(--text-muted)" }} />
                </button>
              </div>

              {/* Per-caption style picker dropdown */}
              {stylePickerForId === caption.id && (
                <div
                  className="mt-1 p-1.5 rounded grid grid-cols-4 gap-1"
                  style={{ background: "var(--bg-app)", border: "1px solid var(--border)" }}
                  onClick={(e) => e.stopPropagation()}
                >
                  {THEME_NAMES.map((t) => {
                    const s = CAPTION_THEMES[t.id];
                    return (
                      <button
                        key={t.id}
                        className="px-1 py-1 rounded text-[8px] text-center transition-all"
                        style={{
                          background: caption.theme === t.id ? "var(--accent)" : "var(--bg-panel-dark)",
                          color: caption.theme === t.id ? "#fff" : s?.color || "var(--text-muted)",
                          fontWeight: s?.bold ? 700 : 400,
                          border: "1px solid var(--border)",
                        }}
                        onClick={() => handleApplyThemeToCaption(caption.id, t.id)}
                        title={t.label}
                      >
                        {t.label}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Bottom toolbar */}
      <div
        className="flex items-center gap-1 px-2 py-1.5 shrink-0"
        style={{ borderTop: "1px solid var(--border)", background: "var(--bg-panel-dark)" }}
      >
        <button className="btn-ghost flex items-center gap-1" onClick={handleAddCaption}>
          <Plus size={12} /> Add
        </button>

        {selectedIds.size > 0 && (
          <button className="btn-ghost flex items-center gap-1" onClick={deleteSelected}>
            <Trash2 size={12} /> Delete
          </button>
        )}

        {captions.length > 0 && (
          <button
            className="btn-ghost flex items-center gap-1"
            onClick={() => handleApplyThemeToAll(useEditorStore.getState().theme)}
            title="Apply current theme to all captions"
          >
            <Palette size={12} /> Apply All
          </button>
        )}

        <div className="flex-1" />

        <button className="btn-ghost" onClick={exportSRT} title="Export SRT">
          SRT
        </button>
        <button className="btn-ghost" onClick={exportASS} title="Export ASS">
          ASS
        </button>
      </div>
    </div>
  );
}
