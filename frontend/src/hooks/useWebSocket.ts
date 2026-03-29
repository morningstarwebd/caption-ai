/* useWebSocket — real-time pipeline progress */

"use client";

import { useEffect, useRef, useCallback } from "react";
import { useEditorStore } from "@/store/editorStore";
import { createProgressWebSocket } from "@/lib/api";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const { jobId, setPipelineProgress } = useEditorStore();

  useEffect(() => {
    if (!jobId) return;

    wsRef.current = createProgressWebSocket(
      jobId,
      (data) => {
        setPipelineProgress(data.status, data.percent);
      },
      () => {
        wsRef.current = null;
      }
    );

    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [jobId, setPipelineProgress]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  return { disconnect };
}
