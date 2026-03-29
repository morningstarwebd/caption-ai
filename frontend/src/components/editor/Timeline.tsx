/* Timeline — main timeline panel with ruler, tracks, playhead */

"use client";

import React, { useRef, useCallback } from "react";
import { Plus, Magnet, ZoomIn, ZoomOut, Trash2 } from "lucide-react";
import { useTimelineStore } from "@/store/timelineStore";
import { useCaptionStore } from "@/store/captionStore";
import { useTimelineSync } from "@/hooks/useTimelineSync";
import TimelineRuler from "./TimelineRuler";
import TimelineTrack from "./TimelineTrack";
import Playhead from "./Playhead";

export default function Timeline() {
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    tracks,
    scrollLeft,
    setScrollLeft,
    snapEnabled,
    toggleSnap,
    zoomIn,
    zoomOut,
    addTrack,
  } = useTimelineStore();

  const clearAll = useCaptionStore((s) => s.clearAll);

  const { handleTimelineSeek } = useTimelineSync();

  // Horizontal scroll
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        // Ctrl+Wheel = zoom
        e.preventDefault();
        if (e.deltaY < 0) zoomIn();
        else zoomOut();
      } else {
        // Normal scroll = horizontal pan
        setScrollLeft(scrollLeft + e.deltaY);
      }
    },
    [scrollLeft, setScrollLeft, zoomIn, zoomOut]
  );

  // Click on ruler area to seek
  const handleRulerClick = useCallback(
    (e: React.MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      handleTimelineSeek(e.clientX, rect.left + 80); // 80 = track header width
    },
    [handleTimelineSeek]
  );

  const handleAddCaptionTrack = useCallback(() => {
    const captionTracks = tracks.filter((t) => t.type === "caption");
    const nextId = `c${captionTracks.length + 1}`;
    addTrack({
      id: nextId,
      type: "caption",
      label: nextId.toUpperCase(),
      locked: false,
      visible: true,
      height: 36,
    });
  }, [tracks, addTrack]);

  const containerWidth = containerRef.current?.clientWidth || 800;

  return (
    <div className="panel flex flex-col h-full">
      {/* Timeline header */}
      <div className="panel-header justify-between">
        <span>Timeline</span>
        <div className="flex items-center gap-1">
          <button
            className="p-1 rounded hover:bg-white/10"
            onClick={toggleSnap}
            title={`Snap ${snapEnabled ? "ON" : "OFF"}`}
          >
            <Magnet
              size={12}
              style={{ color: snapEnabled ? "var(--accent)" : "var(--text-muted)" }}
            />
          </button>
          <button className="p-1 rounded hover:bg-white/10" onClick={zoomOut} title="Zoom Out (-)">
            <ZoomOut size={12} style={{ color: "var(--text-muted)" }} />
          </button>
          <button className="p-1 rounded hover:bg-white/10" onClick={zoomIn} title="Zoom In (+)">
            <ZoomIn size={12} style={{ color: "var(--text-muted)" }} />
          </button>
          <button
            className="p-1 rounded hover:bg-white/10"
            onClick={clearAll}
            title="Clear All Captions"
          >
            <Trash2 size={12} style={{ color: "var(--text-muted)" }} />
          </button>
          <button
            className="p-1 rounded hover:bg-white/10 flex items-center gap-0.5 text-[10px]"
            style={{ color: "var(--text-muted)" }}
            onClick={handleAddCaptionTrack}
            title="Add Track"
          >
            <Plus size={12} /> Track
          </button>
        </div>
      </div>

      {/* Timeline body */}
      <div
        ref={containerRef}
        className="flex-1 overflow-hidden relative"
        onWheel={handleWheel}
        data-timeline-area
      >
        {/* Ruler row */}
        <div className="flex">
          {/* Track header spacer */}
          <div
            className="shrink-0"
            style={{
              width: 80,
              background: "var(--bg-panel-dark)",
              borderRight: "1px solid var(--border)",
              borderBottom: "1px solid var(--border)",
              height: 24,
            }}
          />
          {/* Ruler */}
          <div className="flex-1 overflow-hidden cursor-pointer" onClick={handleRulerClick}>
            <TimelineRuler width={containerWidth - 80} />
          </div>
        </div>

        {/* Tracks */}
        <div className="relative">
          {tracks.map((track) => (
            <TimelineTrack key={track.id} track={track} />
          ))}

          {/* Playhead spans all tracks */}
          <Playhead />

          {/* Empty state */}
          {tracks.length === 0 && (
            <div className="flex items-center justify-center py-8">
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                Import media to start editing
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
