/* Headless Render Page — pixel-perfect caption frame capture for export */

"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Caption, CaptionStyle, CaptionTheme, CAPTION_THEMES } from "@/lib/types";

// ── Highlight colors per theme (same as CaptionOverlay) ──
const HIGHLIGHT_COLORS: Record<string, string> = {
  viral_shorts: "#FFD700",
  kalakar_fire: "#ff6b35",
  karaoke_neon: "#00ff88",
  neon_glow: "#00ffff",
  gradient_wave: "#ff6ec7",
  comic_pop: "#FFD700",
};

// ── Global state exposed to Playwright ──
interface RenderState {
  captions: Caption[];
  theme: CaptionTheme;
  currentTime: number;
  resolution: { width: number; height: number };
  ready: boolean;
}

const DEFAULT_STATE: RenderState = {
  captions: [],
  theme: "viral_shorts",
  currentTime: 0,
  resolution: { width: 1920, height: 1080 },
  ready: false,
};

export default function RenderPage() {
  const [state, setState] = useState<RenderState>(DEFAULT_STATE);

  // ── Expose control functions to window (called by Playwright) ──
  useEffect(() => {
    const win = window as any;

    win.setCaptionData = (captionsJson: string, theme: string, resWidth?: number, resHeight?: number) => {
      try {
        const captions = JSON.parse(captionsJson) as Caption[];
        setState((prev) => ({
          ...prev,
          captions,
          theme: (theme || "viral_shorts") as CaptionTheme,
          resolution: {
            width: resWidth || 1920,
            height: resHeight || 1080,
          },
          ready: true,
        }));
        return true;
      } catch (e) {
        console.error("setCaptionData error:", e);
        return false;
      }
    };

    win.setCaptionTime = (time: number) => {
      setState((prev) => ({ ...prev, currentTime: time }));
      return true;
    };

    win.isReady = () => state.ready;

    // Force transparent background for screenshotting
    document.body.style.background = "transparent";
    document.documentElement.style.background = "transparent";

    // Signal that the page has loaded
    win.__RENDER_PAGE_LOADED__ = true;

    return () => {
      delete win.setCaptionData;
      delete win.setCaptionTime;
      delete win.isReady;
      delete win.__RENDER_PAGE_LOADED__;
      document.body.style.background = "";
      document.documentElement.style.background = "";
    };
  }, [state.ready]);

  const { captions, currentTime, theme, resolution } = state;

  // ── Find active caption at current time ──
  const activeCaption = captions.find(
    (c) => currentTime >= c.start && currentTime <= c.end
  );

  if (!activeCaption) {
    return (
      <div
        id="render-frame"
        style={{
          width: resolution.width,
          height: resolution.height,
          position: "relative",
          background: "transparent",
        }}
      />
    );
  }

  // ── Resolve theme style ──
  const themeStyle: CaptionStyle =
    activeCaption.style || CAPTION_THEMES[activeCaption.theme] || CAPTION_THEMES.minimal;

  // ── Position ──
  const positionStyle: React.CSSProperties = {
    position: "absolute",
    left: 0,
    right: 0,
    display: "flex",
    justifyContent: "center",
    paddingLeft: 40,
    paddingRight: 40,
  };

  if (themeStyle.position === "bottom") {
    positionStyle.bottom = "8%";
  } else if (themeStyle.position === "top") {
    positionStyle.top = "8%";
  } else {
    // center
    positionStyle.top = "50%";
    positionStyle.transform = "translateY(-50%)";
  }

  // ── Text shadow from outline + shadow ──
  const textShadowParts: string[] = [];
  if (themeStyle.outline && themeStyle.outlineColor) {
    const c = themeStyle.outlineColor;
    textShadowParts.push(
      `2px 2px 0 ${c}`, `-2px -2px 0 ${c}`,
      `2px -2px 0 ${c}`, `-2px 2px 0 ${c}`,
      `1px 1px 0 ${c}`, `-1px -1px 0 ${c}`,
      `1px -1px 0 ${c}`, `-1px 1px 0 ${c}`
    );
  }
  if (themeStyle.shadow && themeStyle.shadow !== "none") {
    textShadowParts.push(themeStyle.shadow);
  }

  // Full resolution font size (NO preview scale factor)
  const fontSize = themeStyle.fontSize || 24;
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

  // ── Word-by-word rendering (exact match to CaptionOverlay) ──
  if (activeCaption.words && activeCaption.words.length > 0) {
    const highlightColor = HIGHLIGHT_COLORS[activeCaption.theme] || "#FFD700";
    const normalColor = hasGradient
      ? "transparent"
      : isOutlineBold
      ? "transparent"
      : themeStyle.color || "#ffffff";

    return (
      <div
        id="render-frame"
        style={{
          width: resolution.width,
          height: resolution.height,
          position: "relative",
          background: "transparent",
          overflow: "hidden",
        }}
      >
        <div style={positionStyle}>
          <div
            style={{
              maxWidth: "85%",
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: "0 0.3em",
              alignItems: "baseline",
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
          >
            {activeCaption.words.map((word, idx) => {
              const isSpoken = currentTime >= word.start;
              const isActive = currentTime >= word.start && currentTime < word.end;

              return (
                <span
                  key={`w${idx}`}
                  style={{
                    ...baseWordStyle,
                    fontSize: `${fontSize}px`,
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
                    // No transition — instant state for screenshot capture
                    transition: "none",
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
      </div>
    );
  }

  // ── Fallback: full text (no word data) ──
  const captionStyle: React.CSSProperties = {
    fontSize: `${fontSize}px`,
    ...baseWordStyle,
    color: hasGradient ? "transparent" : isOutlineBold ? "transparent" : themeStyle.color || "#fff",
    backgroundColor: hasGradient ? undefined : themeStyle.backgroundColor || "transparent",
    borderRadius: themeStyle.borderRadius || "4px",
    padding: themeStyle.padding || "6px 12px",
    textAlign: "center" as const,
    lineHeight: 1.3,
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
      id="render-frame"
      style={{
        width: resolution.width,
        height: resolution.height,
        position: "relative",
        background: "transparent",
        overflow: "hidden",
      }}
    >
      <div style={positionStyle}>
        <div style={{ maxWidth: "85%", ...captionStyle }}>
          {activeCaption.text}
        </div>
      </div>
    </div>
  );
}
