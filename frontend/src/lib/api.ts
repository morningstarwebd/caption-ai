/* API client for Caption AI backend */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function uploadVideo(
  file: File,
  language: string = "auto"
): Promise<{ job_id: string }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_lang", language);

  const res = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }

  return res.json();
}

export async function getJob(jobId: string) {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error("Failed to fetch job");
  return res.json();
}

export async function getJobs() {
  const res = await fetch(`${API_BASE}/api/jobs`);
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error("Server unreachable");
  return res.json();
}

export function createProgressWebSocket(
  jobId: string,
  onMessage: (data: { status: string; percent: number; details: string }) => void,
  onClose?: () => void
): WebSocket {
  const wsBase = API_BASE.replace(/^http/, "ws");
  const ws = new WebSocket(`${wsBase}/api/jobs/${jobId}/ws`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      // ignore parse errors
    }
  };

  ws.onclose = () => onClose?.();
  ws.onerror = () => ws.close();

  return ws;
}

export function getVideoStreamUrl(jobId: string): string {
  return `${API_BASE}/api/jobs/${jobId}/video`;
}

export async function exportBurnedMp4(jobId: string, assContent: string, resolution: string = "1080p"): Promise<Blob> {
  const formData = new FormData();
  formData.append("ass_content", assContent);
  formData.append("resolution", resolution);
  formData.append("render_mode", "ass");

  const res = await fetch(`${API_BASE}/api/jobs/${jobId}/export`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Export failed");
  }

  return res.blob();
}

/**
 * Pixel-perfect headless browser export.
 * Sends raw captions JSON + theme so the backend can render frames
 * using the exact same CSS styling as the editor preview.
 */
export async function exportHeadless(
  jobId: string,
  captionsJson: string,
  theme: string,
  resolution: string = "1080p"
): Promise<Blob> {
  const formData = new FormData();
  formData.append("captions_json", captionsJson);
  formData.append("theme", theme);
  formData.append("resolution", resolution);
  formData.append("render_mode", "headless");

  const res = await fetch(`${API_BASE}/api/jobs/${jobId}/export`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Headless export failed");
  }

  return res.blob();
}
