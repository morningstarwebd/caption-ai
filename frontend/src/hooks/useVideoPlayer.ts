/* useVideoPlayer — manages HTML5 video element sync with playback store */

"use client";

import { useCallback, useEffect, useRef } from "react";
import { usePlaybackStore } from "@/store/playbackStore";

export function useVideoPlayer() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const animFrameRef = useRef<number>(0);

  const {
    isPlaying,
    volume,
    playbackRate,
    pause,
    setCurrentTime,
    setDuration,
  } = usePlaybackStore();

  // Sync video element with store
  const attachVideo = useCallback(
    (el: HTMLVideoElement | null) => {
      videoRef.current = el;
      if (!el) return;

      el.volume = volume;
      el.playbackRate = playbackRate;

      el.onloadedmetadata = () => {
        setDuration(el.duration);
      };

      el.onended = () => {
        pause();
      };
    },
    [volume, playbackRate, setDuration, pause]
  );

  // Play/pause sync
  useEffect(() => {
    const el = videoRef.current;
    if (!el) return;

    if (isPlaying) {
      el.play().catch(() => pause());

      // RAF loop for smooth time updates
      const tick = () => {
        setCurrentTime(el.currentTime);
        animFrameRef.current = requestAnimationFrame(tick);
      };
      animFrameRef.current = requestAnimationFrame(tick);
    } else {
      el.pause();
      cancelAnimationFrame(animFrameRef.current);
    }

    return () => cancelAnimationFrame(animFrameRef.current);
  }, [isPlaying, pause, setCurrentTime]);

  // Volume sync
  useEffect(() => {
    if (videoRef.current) videoRef.current.volume = volume;
  }, [volume]);

  // Playback rate sync
  useEffect(() => {
    if (videoRef.current) videoRef.current.playbackRate = playbackRate;
  }, [playbackRate]);

  // Seek when currentTime changes externally (e.g., timeline scrub)
  const seekTo = useCallback(
    (time: number) => {
      setCurrentTime(time);
      if (videoRef.current) {
        videoRef.current.currentTime = time;
      }
    },
    [setCurrentTime]
  );

  // Frame step (1/30s)
  const frameForward = useCallback(() => {
    const ct = videoRef.current?.currentTime || 0;
    seekTo(Math.min((videoRef.current?.duration || 0), ct + 1 / 30));
  }, [seekTo]);

  const frameBack = useCallback(() => {
    const ct = videoRef.current?.currentTime || 0;
    seekTo(Math.max(0, ct - 1 / 30));
  }, [seekTo]);

  return {
    videoRef,
    attachVideo,
    seekTo,
    frameForward,
    frameBack,
  };
}
