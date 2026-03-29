/* CaptionBlock — individual caption block on timeline */

"use client";

import React, { useCallback, useRef } from "react";
import { Caption } from "@/lib/types";
import { useCaptionStore } from "@/store/captionStore";
import { useTimelineStore } from "@/store/timelineStore";
import { useEditorStore } from "@/store/editorStore";
import { timeToPixel, pixelToTime } from "@/lib/timelineUtils";

interface Props {
  caption: Caption;
}

export default function CaptionBlock({ caption }: Props) {
  const { selectedIds, selectCaption, setEditingId, updateCaption, splitCaption } =
    useCaptionStore();
  const { pixelsPerSecond, scrollLeft } = useTimelineStore();
  const activeTool = useEditorStore((s) => s.activeTool);

  const left = timeToPixel(caption.start, pixelsPerSecond, scrollLeft);
  const width = (caption.end - caption.start) * pixelsPerSecond;
  const isSelected = selectedIds.has(caption.id);

  const dragRef = useRef<{ type: "move" | "left" | "right"; startX: number; origStart: number; origEnd: number } | null>(null);

  const handleMouseDown = useCallback(
    (e: React.MouseEvent, type: "move" | "left" | "right") => {
      e.stopPropagation();
      e.preventDefault();

      // Razor tool — split caption at click position
      if (activeTool === "razor" && type === "move") {
        const container = (e.target as HTMLElement).closest("[data-timeline-area]");
        if (!container) return;
        const rect = container.getBoundingClientRect();
        const localX = e.clientX - rect.left + scrollLeft;
        const splitTime = pixelToTime(localX, pixelsPerSecond);
        splitCaption(caption.id, splitTime);
        return;
      }

      dragRef.current = {
        type,
        startX: e.clientX,
        origStart: caption.start,
        origEnd: caption.end,
      };

      const onMove = (ev: MouseEvent) => {
        if (!dragRef.current) return;
        const dx = ev.clientX - dragRef.current.startX;
        const dt = dx / pixelsPerSecond;

        if (dragRef.current.type === "move") {
          const newStart = Math.max(0, dragRef.current.origStart + dt);
          const duration = dragRef.current.origEnd - dragRef.current.origStart;
          updateCaption(caption.id, {
            start: newStart,
            end: newStart + duration,
          });
        } else if (dragRef.current.type === "left") {
          const newStart = Math.max(0, Math.min(caption.end - 0.1, dragRef.current.origStart + dt));
          updateCaption(caption.id, { start: newStart });
        } else {
          const newEnd = Math.max(caption.start + 0.1, dragRef.current.origEnd + dt);
          updateCaption(caption.id, { end: newEnd });
        }
      };

      const onUp = () => {
        dragRef.current = null;
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);
      };

      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    },
    [caption, pixelsPerSecond, scrollLeft, activeTool, updateCaption, splitCaption]
  );

  const langClass =
    caption.lang === "english"
      ? "lang-en"
      : caption.lang === "hindi"
      ? "lang-hi"
      : caption.lang === "bengali"
      ? "lang-bn"
      : "lang-hinglish";

  if (left + width < 0) return null;

  return (
    <div
      className={`caption-block ${langClass} ${isSelected ? "selected" : ""}`}
      style={{
        left: Math.max(0, left),
        width: Math.max(20, width),
        cursor: activeTool === "razor" ? "crosshair" : "grab",
      }}
      onClick={(e) => {
        e.stopPropagation();
        selectCaption(caption.id, e.ctrlKey || e.metaKey);
      }}
      onDoubleClick={() => setEditingId(caption.id)}
      onMouseDown={(e) => handleMouseDown(e, "move")}
    >
      {/* Left resize handle */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-white/20"
        onMouseDown={(e) => handleMouseDown(e, "left")}
      />

      {/* Text */}
      <span className="text-[10px] leading-tight">{caption.text}</span>

      {/* Right resize handle */}
      <div
        className="absolute right-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-white/20"
        onMouseDown={(e) => handleMouseDown(e, "right")}
      />
    </div>
  );
}
