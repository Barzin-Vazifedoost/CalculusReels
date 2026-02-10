'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { CalculusReel } from '@/app/data/calculusReels';
import TopicCard from './TopicCard';
import AudioVisualizer from './AudioVisualizer';
import ProgressBar from './ProgressBar';

interface ReelCardProps {
  reel: CalculusReel;
  isActive: boolean;
  index: number;
  total: number;
  hasInteracted: boolean;
}

const difficultyConfig = {
  beginner: { label: 'Beginner', bg: 'bg-emerald-500/90', text: 'text-white' },
  intermediate: { label: 'Intermediate', bg: 'bg-amber-500/90', text: 'text-white' },
  advanced: { label: 'Advanced', bg: 'bg-rose-500/90', text: 'text-white' },
} as const;

export default function ReelCard({ reel, isActive, index, total, hasInteracted }: ReelCardProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [hasError, setHasError] = useState(false);
  const difficulty = difficultyConfig[reel.difficulty];

  // Auto-play/pause when active state changes
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isActive && hasInteracted) {
      // Reset error state when becoming active
      setHasError(false);
      audio.play().catch(() => {});
      setIsPlaying(true);
    } else {
      audio.pause();
      setIsPlaying(false);
    }
  }, [isActive, hasInteracted]);

  // Track playback progress and handle errors
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTimeUpdate = () => setCurrentTime(audio.currentTime);
    const onLoadedMetadata = () => {
      setDuration(audio.duration);
      setHasError(false); // Reset error on successful load
    };
    const onEnded = () => setIsPlaying(false);
    const onError = () => {
      console.log('Audio error occurred');
      setHasError(true);
    };
    const onCanPlayThrough = () => setHasError(false); // Reset error when audio is ready

    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('error', onError);
    audio.addEventListener('canplaythrough', onCanPlayThrough);

    // Try to load the audio
    audio.load();

    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('loadedmetadata', onLoadedMetadata);
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('error', onError);
      audio.removeEventListener('canplaythrough', onCanPlayThrough);
    };
  }, [reel.audioUrl]);

  const togglePlay = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      audio.play().catch(() => {});
      setIsPlaying(true);
    }
  }, [isPlaying]);

  const toggleMute = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.muted = !isMuted;
    setIsMuted(!isMuted);
  }, [isMuted]);

  const handleSeek = useCallback((time: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = time;
    setCurrentTime(time);
  }, []);

  return (
    <article
      className="relative h-screen w-full snap-start snap-always flex items-center justify-center overflow-hidden"
      aria-label={`${reel.title} — ${reel.topic}`}
      aria-setsize={total}
      aria-posinset={index + 1}
    >
      {/* Hidden audio element */}
      <audio ref={audioRef} src={reel.audioUrl} preload={isActive ? 'auto' : 'metadata'} />

      {/* Visual background */}
      <TopicCard reel={reel} />

      {/* Audio visualizer */}
      <AudioVisualizer isPlaying={isPlaying} color={reel.color} />

      {/* Click overlay to toggle play/pause */}
      <button
        onClick={togglePlay}
        className="absolute inset-0 z-10 w-full h-full cursor-pointer focus-ring"
        aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
      >
        <span className="sr-only">{isPlaying ? 'Pause' : 'Play'}</span>
      </button>

      {/* Progress bar */}
      <ProgressBar
        currentTime={currentTime}
        duration={duration}
        onSeek={handleSeek}
        color={reel.color}
      />

      {/* ── Info overlay ── */}
      <div className="absolute bottom-0 left-0 right-0 z-20 p-6 pb-8 bg-gradient-to-t from-black/90 via-black/50 to-transparent pointer-events-none">
        {/* Badges */}
        <div className="flex items-center gap-2 mb-3">
          <span
            className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold ${difficulty.bg} ${difficulty.text}`}
          >
            {difficulty.label}
          </span>
          <span
            className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold text-white"
            style={{ backgroundColor: `${reel.color}E6` }}
          >
            {reel.topic}
          </span>
          <span className="ml-auto text-white/70 text-xs font-medium tabular-nums">
            {reel.duration}
          </span>
        </div>

        {/* Title */}
        <h2 className="text-white text-xl font-bold leading-tight mb-1.5">
          {reel.title}
        </h2>

        {/* Description */}
        <p className="text-white/80 text-sm leading-relaxed max-w-lg">
          {reel.description}
        </p>

        {/* Progress indicator */}
        <div className="mt-4 flex items-center gap-2 text-white/50 text-xs font-medium">
          <span>{index + 1} / {total}</span>
        </div>
      </div>

      {/* ── Control buttons ── */}
      <div className="absolute top-20 right-5 z-30 flex flex-col gap-3">
        <button
          onClick={(e) => {
            e.stopPropagation();
            toggleMute();
          }}
          className={`focus-ring ${
            isMuted
              ? 'bg-red-500/80 hover:bg-red-500/90 border-red-400/50'
              : 'bg-white/10 hover:bg-white/20 border-white/10'
          } text-white rounded-full p-3 backdrop-blur-md border transition-all duration-150`}
          aria-label={isMuted ? 'Unmute audio' : 'Mute audio'}
        >
          {isMuted ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
          )}
        </button>
      </div>

      {/* ── Play/pause indicator ── */}
      {!isPlaying && hasInteracted && (
        <div className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
          <div className="bg-black/40 rounded-full p-5 backdrop-blur-sm">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      )}

      {/* ── Error fallback ── */}
      {hasError && (
        <div className="absolute inset-0 z-30 flex items-center justify-center bg-black/80">
          <div className="text-center text-white/70 p-6">
            <p className="text-lg font-semibold mb-3">Audio not yet generated</p>
            <p className="text-sm mb-4">Run the generation script or create it manually in NotebookLM</p>
            <a
              href={reel.sourceVideoUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block text-blue-400 hover:text-blue-300 underline text-sm transition-colors"
            >
              Watch on YouTube instead
            </a>
          </div>
        </div>
      )}
    </article>
  );
}
