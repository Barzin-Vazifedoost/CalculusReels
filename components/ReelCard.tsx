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
  isFavorite: boolean;
  onToggleFavorite: (id: number) => void;
}

const difficultyConfig = {
  beginner: { label: 'Beginner', bg: 'bg-emerald-500/90', text: 'text-white' },
  intermediate: { label: 'Intermediate', bg: 'bg-amber-500/90', text: 'text-white' },
  advanced: { label: 'Advanced', bg: 'bg-rose-500/90', text: 'text-white' },
} as const;

export default function ReelCard({ reel, isActive, index, total, hasInteracted, isFavorite, onToggleFavorite }: ReelCardProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [hasError, setHasError] = useState(false);
  const [showLikeAnimation, setShowLikeAnimation] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [videoReady, setVideoReady] = useState(false);
  const lastTapRef = useRef(0);
  const difficulty = difficultyConfig[reel.difficulty];
  const hasVideo = !!reel.videoUrl;
  const SPEED_OPTIONS = [0.75, 1, 1.25, 1.5, 2] as const;

  // Auto-play/pause when active state changes
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isActive && hasInteracted) {
      setHasError(false);
      audio.play().catch(() => {});
      setIsPlaying(true);
    } else {
      audio.pause();
      setIsPlaying(false);
    }
  }, [isActive, hasInteracted]);

  // Sync video with audio playback
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !hasVideo) return;

    if (isActive && hasInteracted) {
      video.play().catch(() => {});
    } else {
      video.pause();
    }
  }, [isActive, hasInteracted, hasVideo]);

  // Track playback progress and handle errors
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTimeUpdate = () => setCurrentTime(audio.currentTime);
    const onLoadedMetadata = () => {
      setDuration(audio.duration);
      setHasError(false);
    };
    const onEnded = () => setIsPlaying(false);
    const onError = () => {
      console.log('Audio error occurred');
      setHasError(true);
    };
    const onCanPlayThrough = () => setHasError(false);

    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('error', onError);
    audio.addEventListener('canplaythrough', onCanPlayThrough);

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
    const video = videoRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
      video?.pause();
      setIsPlaying(false);
    } else {
      audio.play().catch(() => {});
      video?.play().catch(() => {});
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

  const cycleSpeed = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const currentIdx = SPEED_OPTIONS.indexOf(playbackSpeed as typeof SPEED_OPTIONS[number]);
    const nextIdx = (currentIdx + 1) % SPEED_OPTIONS.length;
    const newSpeed = SPEED_OPTIONS[nextIdx];
    audio.playbackRate = newSpeed;
    setPlaybackSpeed(newSpeed);
  }, [playbackSpeed, SPEED_OPTIONS]);

  // Keyboard shortcuts when this reel is active
  useEffect(() => {
    if (!isActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'm' || e.key === 'M') {
        e.preventDefault();
        toggleMute();
      } else if (e.key === ' ') {
        e.preventDefault();
        togglePlay();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isActive, toggleMute, togglePlay]);

  const handleDoubleTap = useCallback(() => {
    const now = Date.now();
    if (now - lastTapRef.current < 300) {
      onToggleFavorite(reel.id);
      if (!isFavorite) {
        setShowLikeAnimation(true);
        setTimeout(() => setShowLikeAnimation(false), 800);
      }
    } else {
      togglePlay();
    }
    lastTapRef.current = now;
  }, [togglePlay, onToggleFavorite, reel.id, isFavorite]);

  const handleShare = useCallback(async () => {
    const shareData = {
      title: reel.title,
      text: `Check out "${reel.title}" on Calculus Reels — ${reel.description}`,
      url: window.location.href,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch {
        // User cancelled or share failed
      }
    } else {
      await navigator.clipboard.writeText(`${shareData.text}\n${shareData.url}`);
    }
  }, [reel]);

  return (
    <article
      className="relative h-screen w-full snap-start snap-always flex items-center justify-center overflow-hidden"
      aria-label={`${reel.title} — ${reel.topic}`}
      aria-setsize={total}
      aria-posinset={index + 1}
    >
      {/* Hidden audio element */}
      <audio ref={audioRef} src={`${process.env.NEXT_PUBLIC_BASE_PATH || ''}${reel.audioUrl}`} preload={isActive ? 'auto' : 'metadata'} />

      {/* Video background (Manim animation) */}
      {hasVideo && (
        <video
          ref={videoRef}
          src={`${process.env.NEXT_PUBLIC_BASE_PATH || ''}${reel.videoUrl}`}
          className={`absolute inset-0 w-full h-full object-contain bg-[#0a0a0a] transition-opacity duration-500 ${videoReady ? 'opacity-100' : 'opacity-0'}`}
          muted
          loop
          playsInline
          preload={isActive ? 'auto' : 'metadata'}
          onCanPlay={() => setVideoReady(true)}
          aria-hidden="true"
        />
      )}

      {/* Static background (when no video or loading) */}
      {(!hasVideo || !videoReady) && <TopicCard reel={reel} />}

      {/* Audio visualizer (only when no video) */}
      {!hasVideo && <AudioVisualizer isPlaying={isPlaying} color={reel.color} />}

      {/* Click overlay to toggle play/pause */}
      <button
        onClick={handleDoubleTap}
        className="absolute inset-0 z-10 w-full h-full cursor-pointer focus-ring"
        aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
      >
        <span className="sr-only">{isPlaying ? 'Pause' : 'Play'}</span>
      </button>

      {/* Double-tap like animation */}
      {showLikeAnimation && (
        <div className="absolute inset-0 z-40 flex items-center justify-center pointer-events-none">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-24 w-24 text-red-500 animate-like-pop"
            fill="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
        </div>
      )}

      {/* Progress bar */}
      <ProgressBar
        currentTime={currentTime}
        duration={duration}
        onSeek={handleSeek}
        color={reel.color}
      />

      {/* Info overlay */}
      <div className="absolute bottom-0 left-0 right-0 z-20 p-6 pb-8 bg-gradient-to-t from-black/90 via-black/50 to-transparent pointer-events-none">
        {/* Badges */}
        <div className="flex items-center gap-2 mb-3 flex-wrap">
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

      {/* Control buttons */}
      <div className="absolute top-20 right-5 z-30 flex flex-col gap-3">
        {/* Mute */}
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

        {/* Favorite */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite(reel.id);
            if (!isFavorite) {
              setShowLikeAnimation(true);
              setTimeout(() => setShowLikeAnimation(false), 800);
            }
          }}
          className={`focus-ring ${
            isFavorite
              ? 'bg-red-500/80 hover:bg-red-500/90 border-red-400/50'
              : 'bg-white/10 hover:bg-white/20 border-white/10'
          } text-white rounded-full p-3 backdrop-blur-md border transition-all duration-150`}
          aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill={isFavorite ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </button>

        {/* Share */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleShare();
          }}
          className="focus-ring bg-white/10 hover:bg-white/20 border-white/10 text-white rounded-full p-3 backdrop-blur-md border transition-all duration-150"
          aria-label="Share this reel"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
        </button>

        {/* Playback speed */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            cycleSpeed();
          }}
          className="focus-ring bg-white/10 hover:bg-white/20 border-white/10 text-white rounded-full p-3 backdrop-blur-md border transition-all duration-150 text-xs font-bold w-11 h-11 flex items-center justify-center"
          aria-label={`Playback speed: ${playbackSpeed}x. Click to change.`}
        >
          {playbackSpeed}x
        </button>
      </div>

      {/* Play/pause indicator */}
      {!isPlaying && hasInteracted && (
        <div className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
          <div className="bg-black/40 rounded-full p-5 backdrop-blur-sm">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      )}

      {/* Error fallback */}
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
