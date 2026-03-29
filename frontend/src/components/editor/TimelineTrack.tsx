/* TimelineTrack — single track row (video, audio, caption) */

"use client";

import React from "react";
import { Lock, Unlock, Eye, EyeOff } from "lucide-react";
import { TimelineTrack as TrackType } from "@/lib/types";
import { useTimelineStore } from "@/store/timelineStore";
import { useEditorStore } from "@/store/editorStore";
import { useCaptionStore } from "@/store/captionStore";
import { usePlaybackStore } from "@/store/playbackStore";
import { timeToPixel } from "@/lib/timelineUtils";
import CaptionBlock from "./CaptionBlock";
import WaveformTrack from "./WaveformTrack";

interface Props {
  track: TrackType;
}

export default function TimelineTrack({ track }: Props) {
  const { toggleTrackLock, toggleTrackVisibility, pixelsPerSecond, scrollLeft } =
    useTimelineStore();
  const { mediaFiles, activeMediaId } = useEditorStore();
  const captions = useCaptionStore((s) => s.captions);
  const duration = usePlaybackStore((s) => s.duration);

  const activeMedia = mediaFiles.find((f) => f.id === activeMediaId);

  return (
    <div
      className="flex"
      style={{
        height: track.height,
        borderBottom: "1px solid var(--border)",
        opacity: track.visible ? 1 : 0.4,
      }}
    >
      {/* Track header */}
      <div
        className="flex items-center gap-1 px-2 shrink-0 select-none"
        style={{
          width: 80,
          background: "var(--bg-panel-dark)",
          borderRight: "1px solid var(--border)",
        }}
      >
        <span className="text-[10px] font-mono font-bold" style={{ color: "var(--text-muted)" }}>
          {track.label}
        </span>
        <div className="flex-1" />
        <button
          className="p-0.5 rounded hover:bg-white/10"
          onClick={() => toggleTrackLock(track.id)}
        >
          {track.locked ? (
            <Lock size={10} style={{ color: "var(--accent)" }} />
          ) : (
            <Unlock size={10} style={{ color: "var(--text-muted)" }} />
          )}
        </button>
        <button
          className="p-0.5 rounded hover:bg-white/10"
          onClick={() => toggleTrackVisibility(track.id)}
        >
          {track.visible ? (
            <Eye size={10} style={{ color: "var(--text-muted)" }} />
          ) : (
            <EyeOff size={10} style={{ color: "var(--text-muted)" }} />
          )}
        </button>
      </div>

      {/* Track content */}
      <div
        className="flex-1 relative overflow-hidden"
        style={{ background: "var(--track-bg)" }}
      >
        {/* Video track */}
        {track.type === "video" && activeMedia && activeMedia.type === "video" && (
          <div
            className="absolute top-1 bottom-1 rounded"
            style={{
              left: timeToPixel(0, pixelsPerSecond, scrollLeft),
              width: duration * pixelsPerSecond,
              background: "linear-gradient(90deg, #2d4a6b 0%, #1e3a5c 100%)",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <span
              className="absolute left-2 top-1/2 -translate-y-1/2 text-[10px] truncate"
              style={{ color: "var(--text-primary)", maxWidth: "90%" }}
            >
              {activeMedia.name}
            </span>
          </div>
        )}

        {/* Audio waveform track */}
        {track.type === "audio" && <WaveformTrack height={track.height} />}

        {/* Caption track */}
        {track.type === "caption" &&
          captions.map((c) => <CaptionBlock key={c.id} caption={c} />)}
      </div>
    </div>
  );
}
