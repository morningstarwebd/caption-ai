/* TimelineRuler — time ruler with ticks */

"use client";

import React from "react";
import { useTimelineStore } from "@/store/timelineStore";
import { getRulerTicks, timeToPixel, formatRulerTime } from "@/lib/timelineUtils";

interface Props {
  width: number;
}

export default function TimelineRuler({ width }: Props) {
  const { pixelsPerSecond, scrollLeft } = useTimelineStore();
  const { major, minor } = getRulerTicks(pixelsPerSecond, width, scrollLeft);

  return (
    <div
      className="relative h-6 shrink-0 select-none"
      style={{ background: "var(--ruler-bg)", borderBottom: "1px solid var(--border)" }}
    >
      {/* Major ticks */}
      {major.map((t) => {
        const x = timeToPixel(t, pixelsPerSecond, scrollLeft);
        if (x < -20 || x > width + 20) return null;
        return (
          <React.Fragment key={`maj-${t}`}>
            <div
              className="absolute top-0 bottom-0 w-px"
              style={{ left: x, background: "rgba(255,255,255,0.2)" }}
            />
            <span
              className="absolute top-1 text-[9px] font-mono"
              style={{ left: x + 3, color: "var(--text-muted)" }}
            >
              {formatRulerTime(t)}
            </span>
          </React.Fragment>
        );
      })}

      {/* Minor ticks */}
      {minor.map((t) => {
        const x = timeToPixel(t, pixelsPerSecond, scrollLeft);
        if (x < 0 || x > width) return null;
        return (
          <div
            key={`min-${t}`}
            className="absolute bottom-0 w-px h-2"
            style={{ left: x, background: "rgba(255,255,255,0.08)" }}
          />
        );
      })}
    </div>
  );
}
