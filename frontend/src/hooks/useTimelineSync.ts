/* useTimelineSync — keeps playhead, video, and timeline in sync */

"use client";

import { useEffect, useCallback } from "react";
import { usePlaybackStore } from "@/store/playbackStore";
import { useTimelineStore } from "@/store/timelineStore";

export function useTimelineSync() {
  const { currentTime, duration } = usePlaybackStore();
  const { pixelsPerSecond, scrollLeft, setScrollLeft } = useTimelineStore();

  // Auto-scroll timeline to keep playhead visible
  useEffect(() => {
    const playheadX = currentTime * pixelsPerSecond;
    const viewportWidth = typeof window !== "undefined" ? window.innerWidth * 0.9 : 800;

    if (playheadX < scrollLeft || playheadX > scrollLeft + viewportWidth) {
      setScrollLeft(Math.max(0, playheadX - viewportWidth * 0.2));
    }
  }, [currentTime, pixelsPerSecond, scrollLeft, setScrollLeft]);

  // Calculate total timeline width
  const totalWidth = Math.max(duration * pixelsPerSecond, 800);

  // Handle timeline click to seek
  const handleTimelineSeek = useCallback(
    (clientX: number, containerLeft: number) => {
      const x = clientX - containerLeft + scrollLeft;
      const time = Math.max(0, Math.min(duration, x / pixelsPerSecond));
      usePlaybackStore.getState().setCurrentTime(time);
    },
    [scrollLeft, pixelsPerSecond, duration]
  );

  return {
    totalWidth,
    handleTimelineSeek,
  };
}
