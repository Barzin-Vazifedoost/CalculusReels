'use client';

import { useEffect, useRef, useState } from 'react';
import ReelCard from '@/components/ReelCard';
import { calculusReels } from './data/calculusReels';

export default function Home() {
  const [currentReelIndex, setCurrentReelIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isScrolling, setIsScrolling] = useState(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;

      // Debounce scroll events
      setIsScrolling(true);
      
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }

      scrollTimeoutRef.current = setTimeout(() => {
        setIsScrolling(false);
        
        // Calculate which reel is currently in view
        const scrollPosition = containerRef.current!.scrollTop;
        const viewportHeight = window.innerHeight;
        const newIndex = Math.round(scrollPosition / viewportHeight);
        
        if (newIndex !== currentReelIndex && newIndex >= 0 && newIndex < calculusReels.length) {
          setCurrentReelIndex(newIndex);
          
          // Snap to the nearest reel
          containerRef.current!.scrollTo({
            top: newIndex * viewportHeight,
            behavior: 'smooth'
          });
        }
      }, 150);
    };

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

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown' && currentReelIndex < calculusReels.length - 1) {
        const newIndex = currentReelIndex + 1;
        setCurrentReelIndex(newIndex);
        containerRef.current?.scrollTo({
          top: newIndex * window.innerHeight,
          behavior: 'smooth'
        });
      } else if (e.key === 'ArrowUp' && currentReelIndex > 0) {
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

  return (
    <main className="relative h-screen w-screen overflow-hidden">
      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-50 p-4 bg-gradient-to-b from-black/60 to-transparent">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <h1 className="text-white text-2xl font-bold">Calculus Reels</h1>
          <span className="text-white/80 text-sm bg-black/40 px-3 py-1 rounded-full backdrop-blur-sm">
            Calc 1ZB3 @ McMaster
          </span>
        </div>
      </header>

      {/* Reels Container */}
      <div 
        ref={containerRef}
        className="h-screen w-screen overflow-y-scroll snap-y snap-mandatory no-scrollbar"
      >
        {calculusReels.map((reel, index) => (
          <ReelCard 
            key={reel.id} 
            reel={reel} 
            isActive={index === currentReelIndex}
          />
        ))}
      </div>

      {/* Navigation Indicators */}
      <div className="absolute right-4 top-1/2 transform -translate-y-1/2 z-50 flex flex-col gap-2">
        {calculusReels.map((reel, index) => (
          <button
            key={reel.id}
            onClick={() => {
              setCurrentReelIndex(index);
              containerRef.current?.scrollTo({
                top: index * window.innerHeight,
                behavior: 'smooth'
              });
            }}
            className={`w-2 h-2 rounded-full transition-all ${
              index === currentReelIndex 
                ? 'bg-white h-8' 
                : 'bg-white/40 hover:bg-white/60'
            }`}
            aria-label={`Go to ${reel.title}`}
          />
        ))}
      </div>

      {/* Instructions overlay (shows on first load) */}
      {currentReelIndex === 0 && (
        <div className="absolute bottom-24 left-0 right-0 z-40 flex justify-center pointer-events-none">
          <div className="bg-black/60 text-white px-4 py-2 rounded-full text-sm backdrop-blur-sm animate-bounce">
            Scroll or use arrow keys to navigate ↓
          </div>
        </div>
      )}
    </main>
  );
}
