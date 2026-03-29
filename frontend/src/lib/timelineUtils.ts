/* Timeline utilities for Caption AI Pro v5.0 */

/**
 * Convert seconds to pixel position given a zoom level.
 * pixelsPerSecond defines the zoom level.
 */
export function timeToPixel(time: number, pixelsPerSecond: number, scrollOffset: number = 0): number {
  return time * pixelsPerSecond - scrollOffset;
}

/**
 * Convert pixel position to time.
 */
export function pixelToTime(pixel: number, pixelsPerSecond: number, scrollOffset: number = 0): number {
  return Math.max(0, (pixel + scrollOffset) / pixelsPerSecond);
}

/**
 * Calculate appropriate ruler tick interval based on zoom level.
 */
export function getRulerTicks(
  pixelsPerSecond: number,
  visibleWidth: number,
  scrollOffset: number = 0
): { major: number[]; minor: number[]; interval: number } {
  // Choose interval so ticks are ~80-150px apart
  const intervals = [0.1, 0.25, 0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300];
  let interval = 1;
  for (const i of intervals) {
    if (i * pixelsPerSecond >= 60) {
      interval = i;
      break;
    }
  }

  const startTime = Math.floor(scrollOffset / pixelsPerSecond / interval) * interval;
  const endTime = (scrollOffset + visibleWidth) / pixelsPerSecond + interval;

  const major: number[] = [];
  const minor: number[] = [];

  for (let t = startTime; t <= endTime; t += interval) {
    if (t >= 0) {
      major.push(t);
      // Add minor ticks (subdivide by 4)
      for (let m = 1; m < 4; m++) {
        const mt = t + (interval / 4) * m;
        if (mt <= endTime && mt >= 0) {
          minor.push(mt);
        }
      }
    }
  }

  return { major, minor, interval };
}

/**
 * Snap time to nearest grid value.
 */
export function snapToGrid(time: number, gridInterval: number): number {
  return Math.round(time / gridInterval) * gridInterval;
}

/**
 * Clamp a value between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

/**
 * Format seconds for ruler display.
 */
export function formatRulerTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds.toFixed(seconds % 1 === 0 ? 0 : 1)}s`;
  }
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}
