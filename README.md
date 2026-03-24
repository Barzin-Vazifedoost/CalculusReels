# Calculus Reels

A TikTok/Instagram Reels-style app for learning Calculus 1ZB3 at McMaster University through short, engaging AI-generated audio content powered by NotebookLM.

**[Live Demo](https://barzin-vazifedoost.github.io/CalculusReels/)**

## Features

- Vertical scroll interface similar to TikTok/Instagram Reels
- 20 AI-generated audio reels covering the full Calc 1ZB3 curriculum
- Touch swipe and keyboard navigation (Arrow keys)
- Double-tap to favorite, with heart animation
- Share reels via native share or clipboard
- Favorites saved to localStorage
- Filter by difficulty (Beginner, Intermediate, Advanced) or topic
- Auto-refresh with configurable intervals
- Audio visualizer with animated equalizer bars
- Interactive progress bar with seek
- Responsive design — mobile-first with collapsible header
- Full accessibility: ARIA labels, skip link, screen reader support, reduced motion

## Topics Covered

| Topic | Count | Difficulty Range |
|-------|-------|-----------------|
| Limits | 3 | Beginner — Advanced |
| Derivatives | 4 | Intermediate — Advanced |
| Integration | 7 | Beginner — Advanced |
| Applications | 4 | Intermediate — Advanced |
| Series | 2 | Advanced |
| Theorems | 1 | Intermediate |

## Tech Stack

- **Next.js 16** — React framework with App Router, static export
- **React 19** — UI components
- **TypeScript** — Type safety
- **Tailwind CSS v4** — Utility-first styling
- **GitHub Pages** — Hosting via GitHub Actions

## Getting Started

### Prerequisites

- Node.js 18+
- npm

### Installation

```bash
git clone https://github.com/Barzin-Vazifedoost/CalculusReels.git
cd CalculusReels
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

- **Tap/click** to play/pause audio
- **Swipe up/down** or use **Arrow keys** to navigate between reels
- **Double-tap** to favorite a reel
- Use the **filter dropdown** to browse by difficulty or topic
- Click **Shuffle** to get a fresh set of reels
- **Share** button copies the link or opens native share sheet on mobile

## Project Structure

```
CalculusReels/
├── app/
│   ├── data/calculusReels.ts   # Reel data, types, and helper functions
│   ├── globals.css             # Global styles and animations
│   ├── layout.tsx              # Root layout with metadata
│   └── page.tsx                # Main feed page (client component)
├── components/
│   ├── ReelCard.tsx            # Individual reel with audio controls
│   ├── AudioVisualizer.tsx     # Animated equalizer bars
│   ├── ProgressBar.tsx         # Interactive audio timeline
│   └── TopicCard.tsx           # Visual background with gradients
├── public/audio/               # 20 MP3 audio files
├── scripts/                    # Audio generation pipeline
└── .github/workflows/          # GitHub Actions deployment
```

## Deployment

The app auto-deploys to GitHub Pages on push to `main` or `develop` via GitHub Actions. See `.github/workflows/deploy.yml`.

## Audio Generation

See [`scripts/README.md`](scripts/README.md) for instructions on generating audio files using NotebookLM, Google Cloud TTS, or Gemini.

## License

ISC

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
