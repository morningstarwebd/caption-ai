/* useCaptionExport — SRT/ASS/TXT export */

"use client";

import { useCallback } from "react";
import { useCaptionStore } from "@/store/captionStore";
import { useEditorStore } from "@/store/editorStore";
import { generateSRT, generateASS, downloadFile } from "@/lib/captionUtils";

export function useCaptionExport() {
  const captions = useCaptionStore((s) => s.captions);
  const theme = useEditorStore((s) => s.theme);

  const exportSRT = useCallback(() => {
    const srt = generateSRT(captions);
    downloadFile(srt, "captions.srt", "text/plain");
  }, [captions]);

  const exportASS = useCallback(() => {
    const ass = generateASS(captions, theme);
    downloadFile(ass, "captions.ass", "text/plain");
  }, [captions, theme]);

  const exportTXT = useCallback(() => {
    const txt = captions
      .sort((a, b) => a.start - b.start)
      .map((c) => c.text)
      .join("\n");
    downloadFile(txt, "captions.txt", "text/plain");
  }, [captions]);

  return { exportSRT, exportASS, exportTXT };
}
