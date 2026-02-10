interface AudioVisualizerProps {
  isPlaying: boolean;
  color: string;
}

const BAR_COUNT = 28;

export default function AudioVisualizer({ isPlaying, color }: AudioVisualizerProps) {
  return (
    <div
      className="absolute bottom-44 left-1/2 -translate-x-1/2 flex items-end gap-[3px] h-12 pointer-events-none"
      aria-hidden="true"
    >
      {Array.from({ length: BAR_COUNT }, (_, i) => (
        <div
          key={i}
          className="w-[3px] rounded-full"
          style={{
            backgroundColor: color,
            opacity: isPlaying ? 0.6 : 0.15,
            height: isPlaying ? undefined : '3px',
            animation: isPlaying
              ? `equalizer 0.6s ease-in-out ${(i * 0.04).toFixed(2)}s infinite alternate`
              : 'none',
            transition: 'opacity 0.3s, height 0.3s',
          }}
        />
      ))}
    </div>
  );
}
