/* MediaPanel — Project files, Effects, History */

"use client";

import React, { useCallback } from "react";
import {
  FolderOpen,
  Film,
  Music,
  Image,
  Plus,
  Trash2,
  Sparkles,
} from "lucide-react";
import { useEditorStore } from "@/store/editorStore";
import { usePlaybackStore } from "@/store/playbackStore";
import { useTimelineStore } from "@/store/timelineStore";
import { MediaFile, CaptionTheme, CAPTION_THEMES } from "@/lib/types";

const THEME_LIST: { id: CaptionTheme; label: string; preview: string }[] = [
  { id: "minimal", label: "Minimal", preview: "Clean subtitles" },
  { id: "viral_shorts", label: "Viral Shorts", preview: "BOLD TEXT" },
  { id: "cinematic", label: "Cinematic", preview: "Golden Cinema" },
  { id: "kalakar_fire", label: "Kalakar Fire", preview: "FIRE 🔥" },
  { id: "karaoke_neon", label: "Karaoke Neon", preview: "Neon Glow" },
  { id: "dramatic", label: "Dramatic", preview: "italic mood" },
  { id: "glassmorphism", label: "Glassmorphism", preview: "Frosted Glass" },
  { id: "retro_vhs", label: "Retro VHS", preview: "VHS TAPE" },
  { id: "neon_glow", label: "Neon Glow", preview: "Purple Neon" },
  { id: "typewriter", label: "Typewriter", preview: "type..." },
  { id: "comic_pop", label: "Comic Pop", preview: "POW!" },
  { id: "elegant_serif", label: "Elegant Serif", preview: "Classic Style" },
  { id: "gradient_wave", label: "Gradient Wave", preview: "Color Flow" },
  { id: "outline_bold", label: "Outline Bold", preview: "STROKE" },
  { id: "shadow_3d", label: "Shadow 3D", preview: "DEPTH" },
  { id: "highlight_box", label: "Highlight Box", preview: "Highlight" },
];

export default function MediaPanel() {
  const {
    mediaFiles,
    activeMediaId,
    addMedia,
    removeMedia,
    setActiveMedia,
    mediaPanelTab,
    setMediaPanelTab,
    theme,
    setTheme,
  } = useEditorStore();

  const setDuration = usePlaybackStore((s) => s.setDuration);
  const initDefaultTracks = useTimelineStore((s) => s.initDefaultTracks);

  const handleImport = useCallback(() => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "video/*,audio/*,image/*";
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      const url = URL.createObjectURL(file);
      const type = file.type.startsWith("video")
        ? "video"
        : file.type.startsWith("audio")
        ? "audio"
        : "image";

      const mediaFile: MediaFile = {
        id: `m_${Date.now()}`,
        name: file.name,
        type: type as MediaFile["type"],
        size: file.size,
        duration: 0,
        url,
        file,
      };

      // Get duration for video/audio
      if (type === "video" || type === "audio") {
        const el = document.createElement(type);
        el.src = url;
        el.onloadedmetadata = () => {
          mediaFile.duration = el.duration;
          if (type === "video") {
            mediaFile.resolution = {
              width: (el as HTMLVideoElement).videoWidth,
              height: (el as HTMLVideoElement).videoHeight,
            };
          }
          addMedia(mediaFile);
          setDuration(el.duration);
          initDefaultTracks();
        };
      } else {
        addMedia(mediaFile);
      }
    };
    input.click();
  }, [addMedia, setDuration, initDefaultTracks]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (!file) return;

      const url = URL.createObjectURL(file);
      const type = file.type.startsWith("video")
        ? "video"
        : file.type.startsWith("audio")
        ? "audio"
        : "image";

      const mediaFile: MediaFile = {
        id: `m_${Date.now()}`,
        name: file.name,
        type: type as MediaFile["type"],
        size: file.size,
        duration: 0,
        url,
        file,
      };

      if (type === "video" || type === "audio") {
        const el = document.createElement(type);
        el.src = url;
        el.onloadedmetadata = () => {
          mediaFile.duration = el.duration;
          if (type === "video") {
            mediaFile.resolution = {
              width: (el as HTMLVideoElement).videoWidth,
              height: (el as HTMLVideoElement).videoHeight,
            };
          }
          addMedia(mediaFile);
          setDuration(el.duration);
          initDefaultTracks();
        };
      } else {
        addMedia(mediaFile);
      }
    },
    [addMedia, setDuration, initDefaultTracks]
  );

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDuration = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  const iconForType = (type: string) => {
    switch (type) {
      case "video": return <Film size={14} />;
      case "audio": return <Music size={14} />;
      default: return <Image size={14} />;
    }
  };

  return (
    <div className="panel flex flex-col h-full">
      {/* Tab header */}
      <div className="panel-header">
        {(["project", "effects", "history"] as const).map((tab) => (
          <div
            key={tab}
            className={`panel-header-tab ${mediaPanelTab === tab ? "active" : ""}`}
            onClick={() => setMediaPanelTab(tab)}
          >
            {tab}
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2">
        {mediaPanelTab === "project" && (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="min-h-full"
          >
            {/* File list */}
            {mediaFiles.map((f) => (
              <div
                key={f.id}
                className="flex items-center gap-2 p-2 rounded cursor-pointer transition-colors mb-1"
                style={{
                  background:
                    activeMediaId === f.id
                      ? "rgba(77, 159, 255, 0.15)"
                      : "transparent",
                  border:
                    activeMediaId === f.id
                      ? "1px solid var(--accent)"
                      : "1px solid transparent",
                }}
                onClick={() => setActiveMedia(f.id)}
              >
                <span style={{ color: "var(--accent)" }}>{iconForType(f.type)}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-xs truncate" style={{ color: "var(--text-primary)" }}>
                    {f.name}
                  </div>
                  <div className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                    {f.duration > 0 && `${formatDuration(f.duration)} · `}
                    {formatSize(f.size)}
                    {f.resolution && ` · ${f.resolution.width}×${f.resolution.height}`}
                  </div>
                </div>
                <button
                  className="p-1 rounded hover:bg-white/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeMedia(f.id);
                  }}
                >
                  <Trash2 size={12} style={{ color: "var(--text-muted)" }} />
                </button>
              </div>
            ))}

            {/* Import button */}
            <button
              className="flex items-center gap-2 w-full p-2 mt-2 rounded text-xs transition-colors"
              style={{
                border: "1px dashed var(--border)",
                color: "var(--text-muted)",
              }}
              onClick={handleImport}
            >
              <Plus size={14} />
              Import Media
            </button>

            {/* Empty state */}
            {mediaFiles.length === 0 && (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <FolderOpen size={32} style={{ color: "var(--text-muted)" }} className="mb-2" />
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                  Drop media here
                  <br />
                  or click Import Media
                </p>
              </div>
            )}
          </div>
        )}

        {mediaPanelTab === "effects" && (
          <div>
            <div className="text-[10px] uppercase tracking-wider mb-2 flex items-center gap-1"
              style={{ color: "var(--text-muted)" }}>
              <Sparkles size={12} />
              Caption Themes ({THEME_LIST.length})
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              {THEME_LIST.map((t) => {
                const s = CAPTION_THEMES[t.id];
                const isOutline = t.id === "outline_bold";
                const hasGrad = !!(s as { gradient?: string }).gradient;
                return (
                  <div
                    key={t.id}
                    className={`style-preview-card ${theme === t.id ? "active" : ""}`}
                    onClick={() => setTheme(t.id)}
                    title={t.label}
                  >
                    <span
                      className="text-xs text-center leading-tight truncate"
                      style={{
                        fontFamily: s?.fontFamily || "Inter",
                        fontWeight: s?.bold ? 700 : 400,
                        fontStyle: s?.italic ? "italic" : "normal",
                        color: hasGrad ? "transparent" : isOutline ? "transparent" : (s?.color || "#fff"),
                        textTransform: (s as { textTransform?: string })?.textTransform as React.CSSProperties["textTransform"] || "none",
                        textShadow: s?.outline
                          ? `1px 1px 0 ${s.outlineColor || "#000"}, -1px -1px 0 ${s.outlineColor || "#000"}`
                          : (s as { shadow?: string })?.shadow || undefined,
                        fontSize: "11px",
                        letterSpacing: (s as { letterSpacing?: string })?.letterSpacing || "normal",
                        ...(hasGrad ? {
                          backgroundImage: (s as { gradient?: string }).gradient,
                          WebkitBackgroundClip: "text",
                          backgroundClip: "text",
                        } : {}),
                        ...(isOutline ? { WebkitTextStroke: "1px #ffffff" } : {}),
                      }}
                    >
                      {t.preview}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {mediaPanelTab === "history" && (
          <div className="py-8 text-center">
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              No history yet
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
