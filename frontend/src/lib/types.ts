/* Types for Caption AI */

export type Language = "auto" | "english" | "hindi" | "hinglish" | "bengali";
export type ToolMode = "selection" | "razor" | "hand" | "zoom";
export type ExportFormat = "mp4" | "srt" | "ass" | "project";

export type CaptionTheme =
  | "minimal"
  | "viral_shorts"
  | "cinematic"
  | "kalakar_fire"
  | "karaoke_neon"
  | "dramatic"
  | "glassmorphism"
  | "retro_vhs"
  | "neon_glow"
  | "typewriter"
  | "comic_pop"
  | "elegant_serif"
  | "gradient_wave"
  | "outline_bold"
  | "shadow_3d"
  | "highlight_box";

export interface MediaFile {
  id: string;
  name: string;
  type: "video" | "audio" | "image";
  size: number;
  duration: number;
  resolution?: { width: number; height: number };
  url: string;
  file: File;
  thumbnail?: string;
}

export interface Caption {
  id: string;
  start: number;
  end: number;
  text: string;
  lang: Language;
  theme: CaptionTheme;
  style?: CaptionStyle;
  words?: AlignedWord[];
}

export interface CaptionStyle {
  fontSize?: number;
  fontFamily?: string;
  color?: string;
  backgroundColor?: string;
  bold?: boolean;
  italic?: boolean;
  outline?: boolean;
  outlineColor?: string;
  position?: "bottom" | "top" | "center";
  textTransform?: "none" | "uppercase" | "lowercase" | "capitalize";
  letterSpacing?: string;
  borderRadius?: string;
  padding?: string;
  backdropBlur?: number;
  gradient?: string;
  shadow?: string;
  animation?: "none" | "fade-in" | "slide-up" | "typewriter" | "pop" | "glow-pulse";
}

export interface TimelineTrack {
  id: string;
  type: "video" | "audio" | "caption";
  label: string;
  locked: boolean;
  visible: boolean;
  height: number;
}

export interface TimelineClip {
  id: string;
  trackId: string;
  start: number;
  end: number;
  mediaId?: string;
  type: "video" | "audio" | "caption";
}

export interface ProjectData {
  version: string;
  timeline: {
    duration: number;
    tracks: TimelineTrack[];
    clips: TimelineClip[];
  };
  captions: Caption[];
  settings: {
    language: Language;
    theme: CaptionTheme;
  };
}

export interface PipelineProgress {
  status: string;
  percent: number;
  details: string;
}

export interface JobResponse {
  job_id: string;
  status: string;
  progress: number;
  filename: string;
  target_lang: string;
  error?: string;
  srt?: string;
  vtt?: string;
  segments?: AlignedSegment[];
  created_at: string;
  completed_at?: string;
}

export interface AlignedSegment {
  start: number;
  end: number;
  text: string;
  words?: AlignedWord[];
}

export interface AlignedWord {
  word: string;
  start: number;
  end: number;
  score: number;
}

// Theme presets
export const CAPTION_THEMES: Record<CaptionTheme, CaptionStyle> = {
  minimal: {
    fontSize: 24,
    fontFamily: "Inter, sans-serif",
    color: "#ffffff",
    backgroundColor: "rgba(0,0,0,0.6)",
    bold: false,
    outline: false,
    position: "bottom",
    borderRadius: "4px",
    padding: "6px 12px",
    animation: "fade-in",
  },
  viral_shorts: {
    fontSize: 36,
    fontFamily: "'Inter', sans-serif",
    color: "#ffffff",
    backgroundColor: "transparent",
    bold: true,
    outline: true,
    outlineColor: "#000000",
    position: "center",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    animation: "pop",
  },
  cinematic: {
    fontSize: 20,
    fontFamily: "'Georgia', serif",
    color: "#f0e68c",
    backgroundColor: "transparent",
    bold: false,
    outline: true,
    outlineColor: "#000000",
    position: "bottom",
    letterSpacing: "0.1em",
    textTransform: "uppercase",
    animation: "fade-in",
  },
  kalakar_fire: {
    fontSize: 40,
    fontFamily: "'Inter', sans-serif",
    color: "#ff6b35",
    backgroundColor: "transparent",
    bold: true,
    outline: true,
    outlineColor: "#000000",
    position: "center",
    textTransform: "uppercase",
    shadow: "0 0 20px rgba(255,107,53,0.8), 0 0 40px rgba(255,107,53,0.4)",
    animation: "pop",
  },
  karaoke_neon: {
    fontSize: 28,
    fontFamily: "'Inter', sans-serif",
    color: "#00ff88",
    backgroundColor: "rgba(0,0,0,0.4)",
    bold: true,
    outline: false,
    position: "bottom",
    borderRadius: "8px",
    padding: "8px 16px",
    shadow: "0 0 10px #00ff88, 0 0 20px #00ff88",
    animation: "glow-pulse",
  },
  dramatic: {
    fontSize: 22,
    fontFamily: "'Georgia', serif",
    color: "#ffffff",
    backgroundColor: "rgba(0,0,0,0.85)",
    bold: false,
    italic: true,
    outline: false,
    position: "bottom",
    borderRadius: "0",
    padding: "10px 20px",
    letterSpacing: "0.08em",
    animation: "fade-in",
  },
  glassmorphism: {
    fontSize: 24,
    fontFamily: "'Inter', sans-serif",
    color: "#ffffff",
    backgroundColor: "rgba(255,255,255,0.1)",
    bold: true,
    outline: false,
    position: "bottom",
    borderRadius: "12px",
    padding: "10px 20px",
    backdropBlur: 12,
    animation: "slide-up",
  },
  retro_vhs: {
    fontSize: 26,
    fontFamily: "'Courier New', monospace",
    color: "#00ffff",
    backgroundColor: "rgba(0,0,0,0.7)",
    bold: true,
    outline: false,
    position: "bottom",
    borderRadius: "0",
    padding: "6px 14px",
    shadow: "3px 3px 0 #ff0066, -1px -1px 0 #00ff66",
    letterSpacing: "0.05em",
    textTransform: "uppercase",
    animation: "none",
  },
  neon_glow: {
    fontSize: 30,
    fontFamily: "'Inter', sans-serif",
    color: "#ff00ff",
    backgroundColor: "transparent",
    bold: true,
    outline: false,
    position: "center",
    shadow: "0 0 7px #ff00ff, 0 0 10px #ff00ff, 0 0 21px #ff00ff, 0 0 42px #bc13fe",
    animation: "glow-pulse",
  },
  typewriter: {
    fontSize: 22,
    fontFamily: "'Courier New', monospace",
    color: "#e0e0e0",
    backgroundColor: "rgba(0,0,0,0.75)",
    bold: false,
    outline: false,
    position: "bottom",
    borderRadius: "2px",
    padding: "8px 16px",
    letterSpacing: "0.12em",
    animation: "typewriter",
  },
  comic_pop: {
    fontSize: 34,
    fontFamily: "'Impact', 'Arial Black', sans-serif",
    color: "#ffff00",
    backgroundColor: "transparent",
    bold: true,
    outline: true,
    outlineColor: "#000000",
    position: "center",
    textTransform: "uppercase",
    shadow: "4px 4px 0 #000",
    animation: "pop",
  },
  elegant_serif: {
    fontSize: 22,
    fontFamily: "'Georgia', 'Times New Roman', serif",
    color: "#f5f0e8",
    backgroundColor: "transparent",
    bold: false,
    italic: true,
    outline: true,
    outlineColor: "rgba(0,0,0,0.6)",
    position: "bottom",
    letterSpacing: "0.15em",
    textTransform: "capitalize",
    animation: "fade-in",
  },
  gradient_wave: {
    fontSize: 32,
    fontFamily: "'Inter', sans-serif",
    color: "#ffffff",
    backgroundColor: "transparent",
    bold: true,
    outline: false,
    position: "center",
    gradient: "linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f97316 100%)",
    animation: "slide-up",
  },
  outline_bold: {
    fontSize: 38,
    fontFamily: "'Inter', sans-serif",
    color: "transparent",
    backgroundColor: "transparent",
    bold: true,
    outline: false,
    position: "center",
    textTransform: "uppercase",
    shadow: "none",
    // Render with -webkit-text-stroke
  },
  shadow_3d: {
    fontSize: 34,
    fontFamily: "'Inter', sans-serif",
    color: "#ffffff",
    backgroundColor: "transparent",
    bold: true,
    outline: false,
    position: "center",
    shadow: "1px 1px 0 #555, 2px 2px 0 #444, 3px 3px 0 #333, 4px 4px 0 #222, 5px 5px 5px rgba(0,0,0,0.5)",
    textTransform: "uppercase",
    animation: "pop",
  },
  highlight_box: {
    fontSize: 26,
    fontFamily: "'Inter', sans-serif",
    color: "#000000",
    backgroundColor: "#facc15",
    bold: true,
    outline: false,
    position: "bottom",
    borderRadius: "4px",
    padding: "6px 14px",
    textTransform: "none",
    animation: "slide-up",
  },
};
