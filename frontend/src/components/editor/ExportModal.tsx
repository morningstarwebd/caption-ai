/* ExportModal — export options dialog */

"use client";

import React, { useState, useRef } from "react";
import { X, Download, Film, FileText, Save, Loader2 } from "lucide-react";
import { useEditorStore } from "@/store/editorStore";
import { useCaptionStore } from "@/store/captionStore";
import { useCaptionExport } from "@/hooks/useCaptionExport";
import { ExportFormat, ProjectData } from "@/lib/types";
import { downloadFile, generateASS } from "@/lib/captionUtils";
import { exportBurnedMp4, exportHeadless, createProgressWebSocket } from "@/lib/api";

interface ExportOption {
  format: ExportFormat;
  label: string;
  description: string;
  icon: React.ReactNode;
}

const options: ExportOption[] = [
  {
    format: "mp4",
    label: "Burned MP4",
    description: "Video with pixel-perfect burned captions",
    icon: <Film size={20} />,
  },
  {
    format: "srt",
    label: "SRT Subtitles",
    description: "Standard subtitle file format",
    icon: <FileText size={20} />,
  },
  {
    format: "ass",
    label: "ASS Subtitles (Styled)",
    description: "Advanced SubStation Alpha with styling",
    icon: <FileText size={20} />,
  },
  {
    format: "project",
    label: "Project File",
    description: "Save as JSON for later editing",
    icon: <Save size={20} />,
  },
];

export default function ExportModal() {
  const { showExportModal, setShowExportModal, language, theme, mediaFiles, jobId } = useEditorStore();
  const allCaptions = useCaptionStore((s) => s.captions);
  const captions = useCaptionStore((s) => s.captions);
  const { exportSRT, exportASS } = useCaptionExport();
  const [exporting, setExporting] = useState(false);
  const [resolution, setResolution] = useState("1080p");
  const [enableKaraoke, setEnableKaraoke] = useState(true);
  const [exportPercent, setExportPercent] = useState(0);
  const [exportStatus, setExportStatus] = useState("");
  const [exportError, setExportError] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  if (!showExportModal) return null;

  const handleExport = async (format: ExportFormat) => {
    setExporting(true);

    switch (format) {
      case "srt":
        exportSRT();
        break;
      case "ass":
        exportASS();
        break;
      case "project": {
        const project: ProjectData = {
          version: "5.0",
          timeline: {
            duration: mediaFiles[0]?.duration || 0,
            tracks: [],
            clips: [],
          },
          captions,
          settings: {
            language: language === "auto" ? "english" : language,
            theme,
          },
        };
        downloadFile(
          JSON.stringify(project, null, 2),
          "caption_ai_project.json",
          "application/json"
        );
        break;
      }
      case "mp4": {
        if (!jobId) {
          alert("No job found. Generate captions first.");
          break;
        }
        if (captions.length === 0) {
          alert("No captions to export.");
          break;
        }
        
        try {
          setExportPercent(0);
          setExportStatus("Preparing pixel-perfect export...");
          setExportError("");

          // Open WebSocket for real-time export progress
          wsRef.current = createProgressWebSocket(
            jobId,
            (data) => {
              if (data.status.startsWith("export")) {
                setExportPercent(Math.max(0, data.percent));
                setExportStatus(data.details || data.status);
              }
            },
            () => { wsRef.current = null; }
          );

          // Pixel-perfect headless export — sends raw captions + theme
          const captionsJson = JSON.stringify(allCaptions);
          const blob = await exportHeadless(jobId, captionsJson, theme, resolution);

          // Cleanup WebSocket
          wsRef.current?.close();
          wsRef.current = null;

          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `captioned_${resolution}_${mediaFiles[0]?.name || "video.mp4"}`;
          a.style.display = "none";
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          setTimeout(() => URL.revokeObjectURL(url), 1500);
        } catch (err: unknown) {
          wsRef.current?.close();
          wsRef.current = null;
          const msg = err instanceof Error ? err.message : "Export failed";
          setExportError(msg);
          setExportPercent(-1);
          setExportStatus("Export failed");
          // Keep modal open to show error — don't close
          setExporting(false);
          return;
        }
        break;
      }
    }

    setExporting(false);
    setShowExportModal(false);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60"
        onClick={() => !exporting && setShowExportModal(false)}
      />

      {/* Modal */}
      <div
        className="relative w-full max-w-md rounded-lg overflow-hidden"
        style={{ background: "var(--bg-panel)", border: "1px solid var(--border)" }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-4 py-3"
          style={{ borderBottom: "1px solid var(--border)" }}
        >
          <div className="flex items-center gap-2">
            <Download size={16} style={{ color: "var(--accent)" }} />
            <span className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
              Export
            </span>
          </div>
          <button
            className="p-1 rounded hover:bg-white/10 disabled:opacity-50"
            disabled={exporting}
            onClick={() => setShowExportModal(false)}
          >
            <X size={16} style={{ color: "var(--text-muted)" }} />
          </button>
        </div>

        {/* Options */}
        <div className="p-4 space-y-2">
          {captions.length === 0 && (
            <div className="text-center py-4">
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                No captions to export. Generate captions first.
              </p>
            </div>
          )}

          {captions.length > 0 &&
            options.map((opt) => (
              <div
                key={opt.format}
                className="flex items-center justify-between w-full p-3 rounded transition-colors text-left"
                style={{
                  background: "var(--bg-panel-dark)",
                  border: "1px solid var(--border)",
                  opacity: exporting ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!exporting) (e.currentTarget as HTMLElement).style.borderColor = "var(--accent)";
                }}
                onMouseLeave={(e) => {
                  if (!exporting) (e.currentTarget as HTMLElement).style.borderColor = "var(--border)";
                }}
              >
                <div 
                  className="flex items-center gap-3 flex-1 cursor-pointer"
                  onClick={() => !exporting && handleExport(opt.format)}
                >
                  <div style={{ color: "var(--accent)" }}>{opt.icon}</div>
                  <div>
                    <div className="text-xs font-medium" style={{ color: "var(--text-primary)" }}>
                      {opt.label}
                    </div>
                    <div className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                      {opt.description}
                    </div>
                  </div>
                </div>

                {opt.format === "mp4" && (
                  <div className="flex items-center gap-2 ml-2">
                    <label className="flex items-center gap-1 cursor-pointer" title="Word-by-word highlight (karaoke effect)">
                      <input
                        type="checkbox"
                        className="accent-[var(--accent)] w-3 h-3"
                        checked={enableKaraoke}
                        onChange={(e) => setEnableKaraoke(e.target.checked)}
                        disabled={exporting}
                      />
                      <span className="text-[9px]" style={{ color: "var(--text-muted)" }}>Karaoke</span>
                    </label>
                    <select
                      className="text-xs px-2 py-1 rounded border-0 outline-none cursor-pointer disabled:opacity-50"
                      style={{ background: "var(--bg-panel)", color: "var(--text-primary)" }}
                      value={resolution}
                      onChange={(e) => setResolution(e.target.value)}
                      disabled={exporting}
                    >
                      <option value="1080p">1080p</option>
                      <option value="720p">720p</option>
                      <option value="480p">480p</option>
                    </select>
                  </div>
                )}
              </div>
            ))}
        </div>

        {/* Footer info & Progress */}
        <div className="px-4 py-3" style={{ borderTop: "1px solid var(--border)" }}>
          {exportError ? (
            <div className="space-y-2">
              <p className="text-xs font-medium" style={{ color: "#ff6b6b" }}>
                {exportError}
              </p>
              <button
                className="text-xs px-3 py-1 rounded"
                style={{ background: "var(--bg-panel-dark)", color: "var(--text-primary)", border: "1px solid var(--border)" }}
                onClick={() => { setExportError(""); setExporting(false); }}
              >
                Try Again
              </button>
            </div>
          ) : exporting ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Loader2 size={12} className="animate-spin" style={{ color: "var(--accent)" }} />
                <p className="text-xs font-medium" style={{ color: "var(--text-primary)" }}>
                  {exportStatus || "Exporting..."} {exportPercent > 0 && exportPercent <= 100 ? `(${exportPercent}%)` : ""}
                </p>
              </div>
              {exportPercent > 0 && exportPercent <= 100 && (
                <div className="h-1.5 rounded-full overflow-hidden w-full" style={{ background: "var(--bg-panel-dark)" }}>
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${exportPercent}%`,
                      background: "var(--accent)",
                    }}
                  />
                </div>
              )}
            </div>
          ) : (
            <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
              {captions.length} caption{captions.length !== 1 ? "s" : ""} ready for export
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
