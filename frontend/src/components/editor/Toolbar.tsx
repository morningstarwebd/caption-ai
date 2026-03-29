/* Toolbar — Premiere Pro-style top toolbar */

"use client";

import React from "react";
import {
  MousePointer2,
  Scissors,
  Hand,
  ZoomIn,
  Undo2,
  Redo2,
  Save,
  Download,
  Circle,
} from "lucide-react";
import { useEditorStore } from "@/store/editorStore";
import { useCaptionStore } from "@/store/captionStore";
import { ToolMode } from "@/lib/types";

const tools: { mode: ToolMode; icon: React.ReactNode; label: string; shortcut: string }[] = [
  { mode: "selection", icon: <MousePointer2 size={16} />, label: "Selection", shortcut: "V" },
  { mode: "razor", icon: <Scissors size={16} />, label: "Razor", shortcut: "C" },
  { mode: "hand", icon: <Hand size={16} />, label: "Hand", shortcut: "H" },
  { mode: "zoom", icon: <ZoomIn size={16} />, label: "Zoom", shortcut: "Z" },
];

export default function Toolbar() {
  const { activeTool, setActiveTool, setShowExportModal } = useEditorStore();
  const { undo, redo } = useCaptionStore();

  return (
    <div
      className="flex items-center h-9 px-2 gap-1 select-none shrink-0"
      style={{ background: "var(--bg-toolbar)", borderBottom: "1px solid var(--border)" }}
    >
      {/* App title */}
      <div className="flex items-center gap-2 mr-4">
        <span className="text-sm font-bold tracking-tight" style={{ color: "var(--accent)" }}>
          Caption AI
        </span>
      </div>

      {/* Menu items */}
      {["File", "Edit", "Sequence", "Captions", "Export"].map((menu) => (
        <button
          key={menu}
          className="px-2 py-1 text-xs rounded hover:bg-white/5 transition-colors"
          style={{ color: "var(--text-muted)" }}
          onClick={() => {
            if (menu === "Export") setShowExportModal(true);
          }}
        >
          {menu}
        </button>
      ))}

      {/* Separator */}
      <div className="w-px h-5 mx-2" style={{ background: "var(--border)" }} />

      {/* Tools */}
      {tools.map((t) => (
        <button
          key={t.mode}
          className="p-1.5 rounded transition-colors"
          style={{
            background: activeTool === t.mode ? "var(--accent)" : "transparent",
            color: activeTool === t.mode ? "white" : "var(--text-muted)",
          }}
          onClick={() => setActiveTool(t.mode)}
          title={`${t.label} (${t.shortcut})`}
        >
          {t.icon}
        </button>
      ))}

      {/* Separator */}
      <div className="w-px h-5 mx-2" style={{ background: "var(--border)" }} />

      {/* Undo/Redo */}
      <button
        className="p-1.5 rounded hover:bg-white/5 transition-colors"
        style={{ color: "var(--text-muted)" }}
        onClick={undo}
        title="Undo (Ctrl+Z)"
      >
        <Undo2 size={16} />
      </button>
      <button
        className="p-1.5 rounded hover:bg-white/5 transition-colors"
        style={{ color: "var(--text-muted)" }}
        onClick={redo}
        title="Redo (Ctrl+Shift+Z)"
      >
        <Redo2 size={16} />
      </button>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right side */}
      <button
        className="p-1.5 rounded hover:bg-white/5 transition-colors"
        style={{ color: "var(--text-muted)" }}
        title="Save Project (Ctrl+S)"
      >
        <Save size={16} />
      </button>
      <button
        className="p-1.5 rounded hover:bg-white/5 transition-colors"
        style={{ color: "var(--text-muted)" }}
        onClick={() => setShowExportModal(true)}
        title="Export (Ctrl+M)"
      >
        <Download size={16} />
      </button>

      {/* Live indicator */}
      <div className="flex items-center gap-1 ml-2">
        <Circle size={8} fill="#4caf76" stroke="none" />
        <span className="text-[10px] font-medium" style={{ color: "var(--accent-green)" }}>
          LIVE
        </span>
      </div>
    </div>
  );
}
