/* WaveformTrack — audio waveform visualization placeholder */

"use client";

import React, { useEffect, useRef } from "react";
import { useEditorStore } from "@/store/editorStore";
import { useTimelineStore } from "@/store/timelineStore";

interface Props {
  height: number;
}

export default function WaveformTrack({ height }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { mediaFiles, activeMediaId } = useEditorStore();
  const { pixelsPerSecond, scrollLeft } = useTimelineStore();

  const activeMedia = mediaFiles.find((f) => f.id === activeMediaId);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, rect.width, rect.height);

    if (!activeMedia || activeMedia.duration === 0) return;

    // Draw a simulated waveform
    const totalWidth = activeMedia.duration * pixelsPerSecond;
    const startPx = Math.max(0, scrollLeft);
    const endPx = Math.min(totalWidth, scrollLeft + rect.width);

    ctx.fillStyle = "#3a7bd5";
    ctx.globalAlpha = 0.6;

    const centerY = rect.height / 2;
    const barWidth = 2;
    const gap = 1;

    for (let x = startPx; x < endPx; x += barWidth + gap) {
      const screenX = x - scrollLeft;
      // Pseudo-random waveform based on position
      const seed = Math.sin(x * 0.05) * Math.cos(x * 0.03) * Math.sin(x * 0.07 + 1);
      const amplitude = (Math.abs(seed) * 0.7 + 0.1) * centerY;

      ctx.fillRect(screenX, centerY - amplitude, barWidth, amplitude * 2);
    }
  }, [activeMedia, pixelsPerSecond, scrollLeft]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full"
      style={{ height }}
    />
  );
}
