/* ProgramMonitor — Video preview with controls and caption overlay */

"use client";

import React, { useRef } from "react";
import {
  Play,
  Pause,
  Square,
  SkipForward,
  SkipBack,
  Eye,
  EyeOff,
  Grid3X3,
} from "lucide-react";
import { usePlaybackStore } from "@/store/playbackStore";
import { useEditorStore } from "@/store/editorStore";
import { useVideoPlayer } from "@/hooks/useVideoPlayer";
import { formatTimecode } from "@/lib/captionUtils";
import CaptionOverlay from "./CaptionOverlay";

export default function ProgramMonitor() {
  const {
    isPlaying,
    currentTime,
    duration,
    zoom,
    quality,
    showSafeZone,
    showCaptionOverlay,
    togglePlayPause,
    stop,
    setZoom,
    setQuality,
    toggleSafeZone,
    toggleCaptionOverlay,
  } = usePlaybackStore();

  const { mediaFiles, activeMediaId } = useEditorStore();
  const { attachVideo, frameForward, frameBack } = useVideoPlayer();
  const videoContainerRef = useRef<HTMLDivElement>(null);

  const activeMedia = mediaFiles.find((f) => f.id === activeMediaId);
  const videoUrl = activeMedia?.type === "video" ? activeMedia.url : null;

  return (
    <div className="panel flex flex-col h-full">
      {/* Header */}
      <div className="panel-header">
        <span>Program</span>
      </div>

      {/* Video area */}
      <div
        ref={videoContainerRef}
        className="flex-1 relative flex items-center justify-center overflow-hidden"
        style={{ background: "#000" }}
      >
        {videoUrl ? (
          <>
            <video
              ref={attachVideo}
              src={videoUrl}
              className="max-w-full max-h-full"
              style={{
                transform: `scale(${zoom / 100})`,
                imageRendering: quality === "quarter" ? "pixelated" : "auto",
              }}
            />

            {/* Safe zone overlay */}
            {showSafeZone && (
              <div className="absolute inset-0 pointer-events-none">
                <div
                  className="absolute border border-dashed border-yellow-500/30"
                  style={{
                    top: "10%",
                    left: "10%",
                    right: "10%",
                    bottom: "10%",
                  }}
                />
                <div
                  className="absolute border border-dashed border-red-500/30"
                  style={{
                    top: "5%",
                    left: "5%",
                    right: "5%",
                    bottom: "5%",
                  }}
                />
              </div>
            )}

            {/* Caption overlay */}
            <CaptionOverlay />
          </>
        ) : (
          <div className="text-center">
            <div className="text-sm mb-1" style={{ color: "var(--text-muted)" }}>
              No media loaded
            </div>
            <div className="text-xs" style={{ color: "var(--text-muted)" }}>
              Import a video to get started
            </div>
          </div>
        )}
      </div>

      {/* Transport controls */}
      <div
        className="flex items-center gap-1 px-3 py-1.5 shrink-0"
        style={{ background: "var(--bg-panel-dark)", borderTop: "1px solid var(--border)" }}
      >
        {/* Playback buttons */}
        <button
          className="p-1 rounded hover:bg-white/10"
          onClick={stop}
          title="Stop"
        >
          <Square size={14} style={{ color: "var(--text-muted)" }} />
        </button>
        <button
          className="p-1 rounded hover:bg-white/10"
          onClick={frameBack}
          title="Frame Back (←)"
        >
          <SkipBack size={14} style={{ color: "var(--text-muted)" }} />
        </button>
        <button
          className="p-1.5 rounded hover:bg-white/10"
          onClick={togglePlayPause}
          title="Play/Pause (Space)"
        >
          {isPlaying ? (
            <Pause size={18} style={{ color: "var(--text-primary)" }} />
          ) : (
            <Play size={18} style={{ color: "var(--text-primary)" }} />
          )}
        </button>
        <button
          className="p-1 rounded hover:bg-white/10"
          onClick={frameForward}
          title="Frame Forward (→)"
        >
          <SkipForward size={14} style={{ color: "var(--text-muted)" }} />
        </button>

        {/* Timecode */}
        <div
          className="font-mono text-xs px-2 py-0.5 rounded ml-2"
          style={{ background: "#000", color: "var(--text-primary)" }}
        >
          {formatTimecode(currentTime)}
        </div>
        <span className="text-[10px] mx-1" style={{ color: "var(--text-muted)" }}>
          /
        </span>
        <div
          className="font-mono text-xs px-2 py-0.5 rounded"
          style={{ background: "#000", color: "var(--text-muted)" }}
        >
          {formatTimecode(duration)}
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* View toggles */}
        <button
          className="p-1 rounded hover:bg-white/10"
          onClick={toggleCaptionOverlay}
          title="Toggle Caption Overlay"
        >
          {showCaptionOverlay ? (
            <Eye size={14} style={{ color: "var(--accent)" }} />
          ) : (
            <EyeOff size={14} style={{ color: "var(--text-muted)" }} />
          )}
        </button>
        <button
          className="p-1 rounded hover:bg-white/10"
          onClick={toggleSafeZone}
          title="Toggle Safe Zone"
        >
          <Grid3X3
            size={14}
            style={{ color: showSafeZone ? "var(--accent)" : "var(--text-muted)" }}
          />
        </button>

        {/* Zoom */}
        <select
          className="text-[10px] px-1 py-0.5 rounded border-0 outline-none cursor-pointer"
          style={{
            background: "var(--bg-panel)",
            color: "var(--text-muted)",
          }}
          value={zoom}
          onChange={(e) => setZoom(Number(e.target.value))}
        >
          <option value={25}>25%</option>
          <option value={50}>50%</option>
          <option value={75}>75%</option>
          <option value={100}>Fit</option>
        </select>

        {/* Quality */}
        <select
          className="text-[10px] px-1 py-0.5 rounded border-0 outline-none cursor-pointer"
          style={{
            background: "var(--bg-panel)",
            color: "var(--text-muted)",
          }}
          value={quality}
          onChange={(e) => setQuality(e.target.value as "full" | "half" | "quarter")}
        >
          <option value="full">Full</option>
          <option value="half">1/2</option>
          <option value="quarter">1/4</option>
        </select>
      </div>
    </div>
  );
}
