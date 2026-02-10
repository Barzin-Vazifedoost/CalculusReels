interface ProgressBarProps {
  currentTime: number;
  duration: number;
  onSeek: (time: number) => void;
  color: string;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function ProgressBar({ currentTime, duration, onSeek, color }: ProgressBarProps) {
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const fraction = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    onSeek(fraction * duration);
  };

  return (
    <div className="absolute bottom-[7.5rem] left-6 right-6 z-30">
      <div className="flex items-center gap-3">
        <span className="text-white/50 text-[11px] font-mono tabular-nums w-10 text-right">
          {formatTime(currentTime)}
        </span>
        <div
          className="flex-1 h-1.5 bg-white/10 rounded-full cursor-pointer relative group"
          onClick={handleClick}
          role="slider"
          aria-label="Audio progress"
          aria-valuenow={Math.round(currentTime)}
          aria-valuemin={0}
          aria-valuemax={Math.round(duration)}
          tabIndex={0}
        >
          <div
            className="absolute top-0 left-0 h-full rounded-full transition-[width] duration-150"
            style={{ width: `${progress}%`, backgroundColor: color }}
          />
          {/* Thumb */}
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ left: `calc(${progress}% - 6px)`, backgroundColor: color }}
          />
        </div>
        <span className="text-white/50 text-[11px] font-mono tabular-nums w-10">
          {formatTime(duration)}
        </span>
      </div>
    </div>
  );
}
