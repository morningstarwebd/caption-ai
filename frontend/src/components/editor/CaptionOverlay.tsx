/* CaptionOverlay — Modern word-by-word caption rendering with pop-in animation */

"use client";

import React from "react";
import { usePlaybackStore } from "@/store/playbackStore";
import { useCaptionStore } from "@/store/captionStore";
import { CAPTION_THEMES, CaptionStyle } from "@/lib/types";

export default function CaptionOverlay() {
  const currentTime = usePlaybackStore((s) => s.currentTime);
  const showOverlay = usePlaybackStore((s) => s.showCaptionOverlay);
  const captions = useCaptionStore((s) => s.captions);

  if (!showOverlay) return null;

  const activeCaption = captions.find(
    (c) => currentTime >= c.start && currentTime <= c.end
  );

  if (!activeCaption) return null;

  const themeStyle: CaptionStyle =
    activeCaption.style || CAPTION_THEMES[activeCaption.theme] || CAPTION_THEMES.minimal;

  const positionStyle: React.CSSProperties = {
    bottom: themeStyle.position === "bottom" ? "8%" : undefined,
    top: themeStyle.position === "top" ? "8%" : undefined,
  };

  if (themeStyle.position === "center") {
    positionStyle.top = "50%";
    positionStyle.transform = "translateY(-50%)";
  }

  // Build text shadow from outline + shadow
  const textShadowParts: string[] = [];
  if (themeStyle.outline && themeStyle.outlineColor) {
    const c = themeStyle.outlineColor;
    textShadowParts.push(`2px 2px 0 ${c}`, `-2px -2px 0 ${c}`, `2px -2px 0 ${c}`, `-2px 2px 0 ${c}`);
  }
  if (themeStyle.shadow && themeStyle.shadow !== "none") {
    textShadowParts.push(themeStyle.shadow);
  }

  const baseFontSize = (themeStyle.fontSize || 24) * 0.55;
  const isOutlineBold = activeCaption.theme === "outline_bold";
  const hasGradient = !!themeStyle.gradient;

  const baseWordStyle: React.CSSProperties = {
    fontFamily: themeStyle.fontFamily,
    fontWeight: themeStyle.bold ? 700 : 400,
    fontStyle: themeStyle.italic ? "italic" : "normal",
    textShadow: textShadowParts.length > 0 ? textShadowParts.join(", ") : undefined,
    textTransform: themeStyle.textTransform || "none",
    letterSpacing: themeStyle.letterSpacing || "normal",
    ...(isOutlineBold ? { WebkitTextStroke: "2px #ffffff" } : {}),
  };

  // ── Word-by-word rendering (modern viral style) ──
  if (activeCaption.words && activeCaption.words.length > 0) {
    // Determine highlight color based on theme
    const highlightColors: Record<string, string> = {
      viral_shorts: "#FFD700",
      kalakar_fire: "#ff6b35",
      karaoke_neon: "#00ff88",
      neon_glow: "#00ffff",
      gradient_wave: "#ff6ec7",
      comic_pop: "#FFD700",
    };
    const highlightColor =
      highlightColors[activeCaption.theme] || "#FFD700";
    const normalColor = hasGradient
      ? "transparent"
      : isOutlineBold
      ? "transparent"
      : themeStyle.color || "#ffffff";

    return (
      <div
        className="absolute left-0 right-0 flex justify-center pointer-events-none px-4"
        style={positionStyle}
      >
        <div
          className="max-w-[85%] flex flex-wrap justify-center gap-x-[0.3em] items-baseline"
          style={{
            backgroundColor: themeStyle.backgroundColor || "transparent",
            borderRadius: themeStyle.borderRadius || "4px",
            padding: themeStyle.padding || "6px 12px",
            ...(themeStyle.backdropBlur
              ? {
                  backdropFilter: `blur(${themeStyle.backdropBlur}px)`,
                  WebkitBackdropFilter: `blur(${themeStyle.backdropBlur}px)`,
                  border: "1px solid rgba(255,255,255,0.15)",
                }
              : {}),
          }}
          key={activeCaption.id}
        >
          {activeCaption.words.map((word, idx) => {
            const isSpoken = currentTime >= word.start;
            const isActive =
              currentTime >= word.start && currentTime < word.end;

            return (
              <span
                key={`${activeCaption.id}-w${idx}`}
                className="word-pop"
                style={{
                  ...baseWordStyle,
                  fontSize: `${baseFontSize}px`,
                  display: "inline-block",
                  color: isActive
                    ? highlightColor
                    : isSpoken
                    ? normalColor
                    : "rgba(255,255,255,0.15)",
                  opacity: isSpoken ? 1 : 0,
                  transform: isSpoken
                    ? isActive
                      ? "scale(1.15) translateY(-1px)"
                      : "scale(1)"
                    : "scale(0.6) translateY(8px)",
                  transition: "all 0.12s cubic-bezier(0.34, 1.56, 0.64, 1)",
                  ...(hasGradient && isSpoken && !isActive
                    ? {
                        backgroundImage: themeStyle.gradient,
                        WebkitBackgroundClip: "text",
                        backgroundClip: "text",
                      }
                    : {}),
                }}
              >
                {word.word}
              </span>
            );
          })}
        </div>
      </div>
    );
  }

  // ── Fallback: no word data, render full text ──
  const animClass =
    themeStyle.animation && themeStyle.animation !== "none"
      ? `caption-anim-${themeStyle.animation}`
      : "";

  const captionStyle: React.CSSProperties = {
    fontSize: `${baseFontSize}px`,
    ...baseWordStyle,
    color: hasGradient
      ? "transparent"
      : isOutlineBold
      ? "transparent"
      : themeStyle.color || "#fff",
    backgroundColor: hasGradient
      ? undefined
      : themeStyle.backgroundColor || "transparent",
    borderRadius: themeStyle.borderRadius || "4px",
    padding: themeStyle.padding || "6px 12px",
    ...(themeStyle.backdropBlur
      ? {
          backdropFilter: `blur(${themeStyle.backdropBlur}px)`,
          WebkitBackdropFilter: `blur(${themeStyle.backdropBlur}px)`,
          border: "1px solid rgba(255,255,255,0.15)",
        }
      : {}),
    ...(hasGradient
      ? {
          backgroundImage: themeStyle.gradient,
          WebkitBackgroundClip: "text",
          backgroundClip: "text",
        }
      : {}),
  };

  return (
    <div
      className="absolute left-0 right-0 flex justify-center pointer-events-none px-4"
      style={positionStyle}
    >
      <div
        className={`max-w-[85%] text-center leading-snug ${animClass}`}
        style={captionStyle}
        key={activeCaption.id}
      >
        {activeCaption.text}
      </div>
    </div>
  );
}
