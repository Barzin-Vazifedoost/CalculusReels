'use client';

import { useEffect, useRef, useState } from 'react';
import ReelCard from '@/components/ReelCard';
import { CalculusReel, getRandomVideoSet, getVideosByDifficulty, getVideosByTopic } from './data/calculusReels';

type FilterMode = 'random' | 'beginner' | 'intermediate' | 'advanced' | 'limits' | 'derivatives' | 'integration' | 'applications' | 'series' | 'theorems';

export default function Home() {
  const [currentReelIndex, setCurrentReelIndex] = useState(0);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(45);
  const [filterMode, setFilterMode] = useState<FilterMode>('random');
  const [currentReels, setCurrentReels] = useState<CalculusReel[]>([]);
  const [lastRefresh, setLastRefresh] = useState(Date.now());
  const containerRef = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [showHint, setShowHint] = useState(true);
  const [nextRefreshIn, setNextRefreshIn] = useState(refreshInterval);
  const [hasInteracted, setHasInteracted] = useState(false);

  const refreshReels = () => {
    let newReels: CalculusReel[];

    switch (filterMode) {
      case 'beginner':
      case 'intermediate':
      case 'advanced':
        newReels = getVideosByDifficulty(filterMode, 8);
        break;
      case 'limits':
      case 'derivatives':
      case 'integration':
      case 'applications':
      case 'series':
      case 'theorems':
        newReels = getVideosByTopic(filterMode, 8);
        break;
      case 'random':
      default:
        newReels = getRandomVideoSet(8);
        break;
    }

    setCurrentReels(newReels);
    setLastRefresh(Date.now());
    setCurrentReelIndex(0);
    setNextRefreshIn(refreshInterval);

    if (containerRef.current) {
      containerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Initialize reels on mount and filter change
  useEffect(() => {
    refreshReels();
  }, [filterMode]);

  // Countdown timer for auto-refresh
  useEffect(() => {
    if (autoRefreshEnabled) {
      const countdownInterval = setInterval(() => {
        setNextRefreshIn(prev => {
          if (prev <= 1) {
            refreshReels();
            return refreshInterval;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(countdownInterval);
    }
  }, [autoRefreshEnabled, refreshInterval]);

  // Hide the scroll hint after 4 seconds or on first scroll
  useEffect(() => {
    const timer = setTimeout(() => setShowHint(false), 4000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;

      setShowHint(false);

      const scrollPosition = containerRef.current.scrollTop;
      const viewportHeight = window.innerHeight;
      const newIndex = Math.round(scrollPosition / viewportHeight);

      if (newIndex !== currentReelIndex && newIndex >= 0 && newIndex < currentReels.length) {
        setCurrentReelIndex(newIndex);
      }

      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }

      scrollTimeoutRef.current = setTimeout(() => {
        if (containerRef.current) {
          containerRef.current.scrollTo({
            top: newIndex * viewportHeight,
            behavior: 'smooth'
          });
        }
      }, 100);
    }

    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll, { passive: true });
    }

    return () => {
      if (container) {
        container.removeEventListener('scroll', handleScroll);
      }
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [currentReelIndex]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown' && currentReelIndex < currentReels.length - 1) {
        e.preventDefault();
        const newIndex = currentReelIndex + 1;
        setCurrentReelIndex(newIndex);
        containerRef.current?.scrollTo({
          top: newIndex * window.innerHeight,
          behavior: 'smooth'
        });
      } else if (e.key === 'ArrowUp' && currentReelIndex > 0) {
        e.preventDefault();
        const newIndex = currentReelIndex - 1;
        setCurrentReelIndex(newIndex);
        containerRef.current?.scrollTo({
          top: newIndex * window.innerHeight,
          behavior: 'smooth'
        });
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentReelIndex]);

  const navigateTo = (index: number) => {
    setCurrentReelIndex(index);
    containerRef.current?.scrollTo({
      top: index * window.innerHeight,
      behavior: 'smooth'
    });
  };

  const handleInteraction = () => {
    if (!hasInteracted) {
      setHasInteracted(true);
    }
  };

  return (
    <>
      {/* Skip link for keyboard / screen-reader users */}
      <a href="#reels" className="skip-link">
        Skip to content
      </a>

      <main className="relative h-screen w-screen overflow-hidden bg-black" onClick={handleInteraction}>
        {/* ── Header ── */}
        <header className="absolute top-0 left-0 right-0 z-50 px-5 py-4 bg-gradient-to-b from-black/80 via-black/50 to-transparent">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <div className="flex items-center gap-3">
              <span className="text-white text-xl font-bold tracking-tight" aria-hidden="true">
                &int;
              </span>
              <h1 className="text-white text-lg font-semibold tracking-tight">
                Calculus Reels
              </h1>
              {autoRefreshEnabled && (
                <span className="text-green-400 text-xs bg-green-500/20 px-2 py-1 rounded-full border border-green-500/30">
                  {nextRefreshIn}s
                </span>
              )}
            </div>

            <div className="flex items-center gap-2">
              {/* Filter Mode Selector */}
              <select
                value={filterMode}
                onChange={(e) => setFilterMode(e.target.value as FilterMode)}
                className="bg-white/10 text-white text-xs px-2 py-1 rounded border border-white/20 backdrop-blur-md"
                aria-label="Filter reels"
              >
                <option value="random">Random Mix</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="limits">Limits</option>
                <option value="derivatives">Derivatives</option>
                <option value="integration">Integration</option>
                <option value="applications">Applications</option>
                <option value="series">Series</option>
                <option value="theorems">Theorems</option>
              </select>

              {/* Auto Refresh Toggle */}
              <button
                onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
                className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                  autoRefreshEnabled
                    ? 'bg-green-500/80 text-white border border-green-400/50'
                    : 'bg-white/10 text-white/80 hover:bg-white/20 border border-white/15'
                } backdrop-blur-md`}
                aria-label={autoRefreshEnabled ? 'Disable auto-refresh' : 'Enable auto-refresh'}
              >
                {autoRefreshEnabled ? 'Auto' : 'Manual'}
              </button>

              {/* Refresh Interval Selector */}
              {autoRefreshEnabled && (
                <select
                  value={refreshInterval}
                  onChange={(e) => {
                    const newInterval = parseInt(e.target.value);
                    setRefreshInterval(newInterval);
                    setNextRefreshIn(newInterval);
                  }}
                  className="bg-white/10 text-white text-xs px-2 py-1 rounded border border-white/20 backdrop-blur-md"
                  aria-label="Refresh interval"
                >
                  <option value={30}>30s</option>
                  <option value={45}>45s</option>
                  <option value={60}>1m</option>
                  <option value={120}>2m</option>
                  <option value={300}>5m</option>
                </select>
              )}

              {/* Manual Refresh Button */}
              <button
                onClick={refreshReels}
                className="bg-white/10 hover:bg-white/20 text-white/80 hover:text-white px-2 py-1 rounded text-xs border border-white/15 backdrop-blur-md transition-all"
                aria-label="Refresh reels"
              >
                Shuffle
              </button>

              <span className="text-white/90 text-xs font-medium bg-white/10 px-2 py-1 rounded border border-white/15 backdrop-blur-md">
                {currentReels.length} reels
              </span>
            </div>
          </div>
        </header>

        {/* ── Reels container ── */}
        <div
          id="reels"
          ref={containerRef}
          className="h-screen w-screen overflow-y-scroll snap-y snap-mandatory no-scrollbar"
          role="feed"
          aria-label="Calculus audio reels"
        >
          {currentReels.map((reel, index) => (
            <ReelCard
              key={`${reel.id}-${lastRefresh}`}
              reel={reel}
              isActive={index === currentReelIndex}
              index={index}
              total={currentReels.length}
              hasInteracted={hasInteracted}
            />
          ))}
        </div>

        {/* ── Navigation dots ── */}
        <nav
          className="absolute right-3 top-1/2 -translate-y-1/2 z-50 flex flex-col items-center gap-1"
          aria-label="Reel navigation"
        >
          {currentReels.map((reel, index) => (
            <button
              key={reel.id}
              onClick={() => navigateTo(index)}
              className={`focus-ring flex items-center justify-center w-11 h-11 rounded-full transition-all duration-200 ${
                index === currentReelIndex ? '' : 'group'
              }`}
              aria-label={`Go to reel ${index + 1}: ${reel.title}`}
              aria-current={index === currentReelIndex ? 'true' : undefined}
            >
              <span
                className={`block rounded-full transition-all duration-200 ${
                  index === currentReelIndex
                    ? 'w-2.5 h-6 bg-white'
                    : 'w-2 h-2 bg-white/40 group-hover:bg-white/70'
                }`}
              />
            </button>
          ))}
        </nav>

        {/* ── Tap to listen overlay (first interaction) ── */}
        {!hasInteracted && (
          <div
            className="absolute inset-0 z-40 flex items-center justify-center bg-black/60 cursor-pointer"
            onClick={handleInteraction}
            role="button"
            aria-label="Tap to start listening"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleInteraction(); }}
          >
            <div className="text-center">
              <div className="bg-white/10 rounded-full p-6 mb-4 inline-block border border-white/20 backdrop-blur-md">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                </svg>
              </div>
              <p className="text-white text-lg font-semibold mb-1">Tap to start listening</p>
              <p className="text-white/60 text-sm">AI-generated audio reels powered by NotebookLM</p>
            </div>
          </div>
        )}

        {/* ── Scroll hint ── */}
        {showHint && hasInteracted && (
          <div
            className="absolute bottom-28 left-0 right-0 z-40 flex justify-center pointer-events-none"
            role="status"
          >
            <div className="bg-white/10 text-white text-sm font-medium px-5 py-2.5 rounded-full border border-white/15 backdrop-blur-md animate-bounce">
              Scroll or press arrow keys to navigate
            </div>
          </div>
        )}

        {/* ── Live region for screen readers ── */}
        <div aria-live="polite" aria-atomic="true" className="sr-only">
          {`Reel ${currentReelIndex + 1} of ${currentReels.length}: ${currentReels[currentReelIndex]?.title || 'Loading...'}`}
        </div>
      </main>
    </>
  );
}
