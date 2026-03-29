/* Playhead — red playhead line on timeline */

"use client";

import React, { useCallback, useRef } from "react";
import { usePlaybackStore } from "@/store/playbackStore";
import { useTimelineStore } from "@/store/timelineStore";
import { timeToPixel } from "@/lib/timelineUtils";

export default function Playhead() {
  const currentTime = usePlaybackStore((s) => s.currentTime);
  const duration = usePlaybackStore((s) => s.duration);
  const setCurrentTime = usePlaybackStore((s) => s.setCurrentTime);
  const { pixelsPerSecond, scrollLeft } = useTimelineStore();

  const draggingRef = useRef(false);

  const x = timeToPixel(currentTime, pixelsPerSecond, scrollLeft);

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      draggingRef.current = true;

      const onMove = (ev: MouseEvent) => {
        if (!draggingRef.current) return;
        const container = (e.target as HTMLElement).closest("[data-timeline-area]");
        if (!container) return;
        const rect = container.getBoundingClientRect();
        const localX = ev.clientX - rect.left + scrollLeft;
        const time = Math.max(0, Math.min(duration, localX / pixelsPerSecond));
        setCurrentTime(time);
      };

      const onUp = () => {
        draggingRef.current = false;
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);
      };

      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    },
    [scrollLeft, pixelsPerSecond, duration, setCurrentTime]
  );

  if (x < -10) return null;

  return (
    <>
      <div className="playhead-line" style={{ left: x }} />
      <div
        className="playhead-head"
        style={{ left: x - 5 }}
        onMouseDown={handleMouseDown}
      />
    </>
  );
}
