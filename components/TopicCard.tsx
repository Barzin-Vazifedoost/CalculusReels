import { CalculusReel } from '@/app/data/calculusReels';

const MATH_SYMBOLS = ['\u222B', '\u03A3', '\u0394', '\u221E', '\u03C0', '\u2202', 'dx', 'dy', 'lim', '\u221A'];

interface TopicCardProps {
  reel: CalculusReel;
}

export default function TopicCard({ reel }: TopicCardProps) {
  return (
    <div className="absolute inset-0 overflow-hidden">
      {/* Gradient background */}
      <div
        className="absolute inset-0"
        style={{
          background: `radial-gradient(ellipse at 30% 20%, ${reel.color}30 0%, transparent 50%),
                       radial-gradient(ellipse at 70% 80%, ${reel.color}20 0%, transparent 50%),
                       linear-gradient(160deg, #0a0a0a 0%, #111111 50%, #0a0a0a 100%)`,
        }}
      />

      {/* Floating math symbols */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        {MATH_SYMBOLS.map((sym, i) => (
          <span
            key={i}
            className="absolute text-white/[0.04] font-mono select-none"
            style={{
              fontSize: `${24 + (i % 4) * 16}px`,
              left: `${(i * 17) % 90 + 5}%`,
              top: `${(i * 23) % 85 + 5}%`,
              transform: `rotate(${(i * 37) % 360}deg)`,
            }}
          >
            {sym}
          </span>
        ))}
      </div>

      {/* Central topic icon */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <span
          className="font-mono font-bold opacity-20 select-none"
          style={{ fontSize: '7rem', color: reel.color }}
          aria-hidden="true"
        >
          {reel.icon}
        </span>
        <span
          className="text-5xl font-black uppercase tracking-[0.3em] opacity-[0.04] text-white mt-4 select-none"
          aria-hidden="true"
        >
          {reel.topic}
        </span>
      </div>
    </div>
  );
}
