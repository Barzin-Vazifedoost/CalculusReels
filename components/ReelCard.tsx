'use client';

import { useRef, useEffect, useState } from 'react';
import { CalculusReel } from '@/app/data/calculusReels';

interface ReelCardProps {
  reel: CalculusReel;
  isActive: boolean;
}

export default function ReelCard({ reel, isActive }: ReelCardProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);

  useEffect(() => {
    if (videoRef.current) {
      if (isActive) {
        videoRef.current.play().catch(err => console.log('Play error:', err));
        setIsPlaying(true);
      } else {
        videoRef.current.pause();
        videoRef.current.currentTime = 0;
        setIsPlaying(false);
      }
    }
  }, [isActive]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setIsPlaying(false);
      } else {
        videoRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const difficultyColors = {
    beginner: 'bg-green-500',
    intermediate: 'bg-yellow-500',
    advanced: 'bg-red-500'
  };

  return (
    <div className="relative h-screen w-full snap-start snap-always flex items-center justify-center bg-black">
      <video
        ref={videoRef}
        className="h-full w-full object-contain"
        loop
        muted={isMuted}
        playsInline
        poster={reel.thumbnail}
        onClick={togglePlay}
      >
        <source src={reel.videoUrl} type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {/* Overlay with video information */}
      <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${difficultyColors[reel.difficulty]} text-white`}>
                {reel.difficulty.toUpperCase()}
              </span>
              <span className="px-2 py-1 rounded-full text-xs font-semibold bg-blue-500 text-white">
                {reel.topic}
              </span>
            </div>
            <h2 className="text-white text-2xl font-bold mb-2">{reel.title}</h2>
            <p className="text-white/90 text-sm mb-2">{reel.description}</p>
            <p className="text-white/70 text-xs">Duration: {reel.duration}</p>
          </div>
        </div>
      </div>

      {/* Control buttons */}
      <div className="absolute top-6 right-6 flex flex-col gap-4">
        <button
          onClick={toggleMute}
          className="bg-black/50 hover:bg-black/70 text-white rounded-full p-3 backdrop-blur-sm transition-all"
          aria-label={isMuted ? "Unmute" : "Mute"}
        >
          {isMuted ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
          )}
        </button>
      </div>

      {/* Play/Pause indicator */}
      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-black/50 rounded-full p-6 backdrop-blur-sm">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      )}
    </div>
  );
}
