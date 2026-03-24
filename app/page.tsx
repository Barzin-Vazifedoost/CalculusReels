'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import ReelCard from '@/components/ReelCard';
import { CalculusReel, getRandomVideoSet, getVideosByDifficulty, getVideosByTopic } from './data/calculusReels';

type FilterMode = 'random' | 'beginner' | 'intermediate' | 'advanced' | 'limits' | 'derivatives' | 'integration' | 'applications' | 'series' | 'theorems';

function useFavorites() {
  const [favorites, setFavorites] = useState<Set<number>>(new Set());

  useEffect(() => {
    try {
      const stored = localStorage.getItem('calculusreels-favorites');
      if (stored) setFavorites(new Set(JSON.parse(stored)));
    } catch {}
  }, []);

  const toggle = useCallback((id: number) => {
    setFavorites(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      try {
        localStorage.setItem('calculusreels-favorites', JSON.stringify([...next]));
      } catch {}
      return next;
    });
  }, []);

  return { favorites, toggle };
}

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
  const [headerExpanded, setHeaderExpanded] = useState(false);
  const { favorites, toggle: toggleFavorite } = useFavorites();

  // Touch/swipe state
  const touchStartY = useRef(0);
  const touchStartTime = useRef(0);

  const refreshReels = useCallback(() => {
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
  }, [filterMode, refreshInterval]);

  // Initialize reels on mount and filter change
  useEffect(() => {
    refreshReels();
  }, [filterMode, refreshReels]);

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
  }, [autoRefreshEnabled, refreshInterval, refreshReels]);

  // Hide the scroll hint after 4 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowHint(false), 4000);
    return () => clearTimeout(timer);
  }, []);

  // Scroll tracking
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
  }, [currentReelIndex, currentReels.length]);

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
  }, [currentReelIndex, currentReels.length]);

  // Touch swipe navigation
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleTouchStart = (e: TouchEvent) => {
      touchStartY.current = e.touches[0].clientY;
      touchStartTime.current = Date.now();
    };

    const handleTouchEnd = (e: TouchEvent) => {
      const deltaY = touchStartY.current - e.changedTouches[0].clientY;
      const deltaTime = Date.now() - touchStartTime.current;
      const velocity = Math.abs(deltaY) / deltaTime;

      // Fast flick (velocity > 0.5px/ms) or significant swipe (> 50px)
      if (velocity > 0.5 || Math.abs(deltaY) > 50) {
        if (deltaY > 0 && currentReelIndex < currentReels.length - 1) {
          const newIndex = currentReelIndex + 1;
          setCurrentReelIndex(newIndex);
          container.scrollTo({ top: newIndex * window.innerHeight, behavior: 'smooth' });
        } else if (deltaY < 0 && currentReelIndex > 0) {
          const newIndex = currentReelIndex - 1;
          setCurrentReelIndex(newIndex);
          container.scrollTo({ top: newIndex * window.innerHeight, behavior: 'smooth' });
        }
      }
    };

    container.addEventListener('touchstart', handleTouchStart, { passive: true });
    container.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [currentReelIndex, currentReels.length]);

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
        {/* Header */}
        <header className="absolute top-0 left-0 right-0 z-50 px-4 sm:px-5 py-3 sm:py-4 bg-gradient-to-b from-black/80 via-black/50 to-transparent">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <div className="flex items-center gap-2 sm:gap-3">
              <span className="text-white text-xl font-bold tracking-tight" aria-hidden="true">
                &int;
              </span>
              <h1 className="text-white text-base sm:text-lg font-semibold tracking-tight">
                Calculus Reels
              </h1>
              {autoRefreshEnabled && (
                <span className="text-green-400 text-[10px] sm:text-xs bg-green-500/20 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full border border-green-500/30">
                  {nextRefreshIn}s
                </span>
              )}
            </div>

            {/* Desktop controls */}
            <div className="hidden sm:flex items-center gap-2">
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

            {/* Mobile menu toggle */}
            <button
              onClick={() => setHeaderExpanded(!headerExpanded)}
              className="sm:hidden bg-white/10 hover:bg-white/20 text-white rounded-lg p-2 border border-white/15 backdrop-blur-md transition-all"
              aria-label="Toggle menu"
              aria-expanded={headerExpanded}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                {headerExpanded ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                )}
              </svg>
            </button>
          </div>

          {/* Mobile expanded controls */}
          {headerExpanded && (
            <div className="sm:hidden mt-3 flex flex-wrap items-center gap-2 max-w-6xl mx-auto">
              <select
                value={filterMode}
                onChange={(e) => {
                  setFilterMode(e.target.value as FilterMode);
                  setHeaderExpanded(false);
                }}
                className="bg-white/10 text-white text-xs px-2 py-1.5 rounded border border-white/20 backdrop-blur-md flex-1 min-w-[100px]"
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

              <button
                onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
                className={`px-2 py-1.5 rounded text-xs font-medium transition-all ${
                  autoRefreshEnabled
                    ? 'bg-green-500/80 text-white border border-green-400/50'
                    : 'bg-white/10 text-white/80 hover:bg-white/20 border border-white/15'
                } backdrop-blur-md`}
              >
                {autoRefreshEnabled ? 'Auto' : 'Manual'}
              </button>

              <button
                onClick={() => {
                  refreshReels();
                  setHeaderExpanded(false);
                }}
                className="bg-white/10 hover:bg-white/20 text-white/80 hover:text-white px-2 py-1.5 rounded text-xs border border-white/15 backdrop-blur-md transition-all"
              >
                Shuffle
              </button>

              <span className="text-white/90 text-xs font-medium bg-white/10 px-2 py-1.5 rounded border border-white/15 backdrop-blur-md">
                {currentReels.length} reels
              </span>
            </div>
          )}
        </header>

        {/* Reels container */}
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
              isFavorite={favorites.has(reel.id)}
              onToggleFavorite={toggleFavorite}
            />
          ))}
        </div>

        {/* Navigation dots */}
        <nav
          className="absolute right-2 sm:right-3 top-1/2 -translate-y-1/2 z-50 flex flex-col items-center gap-0.5 sm:gap-1"
          aria-label="Reel navigation"
        >
          {currentReels.map((reel, index) => (
            <button
              key={reel.id}
              onClick={() => navigateTo(index)}
              className={`focus-ring flex items-center justify-center w-9 h-9 sm:w-11 sm:h-11 rounded-full transition-all duration-200 ${
                index === currentReelIndex ? '' : 'group'
              }`}
              aria-label={`Go to reel ${index + 1}: ${reel.title}`}
              aria-current={index === currentReelIndex ? 'true' : undefined}
            >
              <span
                className={`block rounded-full transition-all duration-200 ${
                  index === currentReelIndex
                    ? 'w-2 h-5 sm:w-2.5 sm:h-6 bg-white'
                    : 'w-1.5 h-1.5 sm:w-2 sm:h-2 bg-white/40 group-hover:bg-white/70'
                }`}
              />
            </button>
          ))}
        </nav>

        {/* Tap to listen overlay */}
        {!hasInteracted && (
          <div
            className="absolute inset-0 z-40 flex items-center justify-center bg-black/60 cursor-pointer"
            onClick={handleInteraction}
            role="button"
            aria-label="Tap to start listening"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleInteraction(); }}
          >
            <div className="text-center px-6">
              <div className="bg-white/10 rounded-full p-6 mb-4 inline-block border border-white/20 backdrop-blur-md">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                </svg>
              </div>
              <p className="text-white text-lg font-semibold mb-1">Tap to start listening</p>
              <p className="text-white/60 text-sm">AI-generated audio reels for Calculus 1ZB3</p>
            </div>
          </div>
        )}

        {/* Scroll hint */}
        {showHint && hasInteracted && (
          <div
            className="absolute bottom-28 left-0 right-0 z-40 flex justify-center pointer-events-none"
            role="status"
          >
            <div className="bg-white/10 text-white text-sm font-medium px-5 py-2.5 rounded-full border border-white/15 backdrop-blur-md animate-bounce">
              Swipe up or press arrow keys to navigate
            </div>
          </div>
        )}

        {/* Live region for screen readers */}
        <div aria-live="polite" aria-atomic="true" className="sr-only">
          {`Reel ${currentReelIndex + 1} of ${currentReels.length}: ${currentReels[currentReelIndex]?.title || 'Loading...'}`}
        </div>
      </main>
    </>
  );
}
