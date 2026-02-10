# CalculusReels

A TikTok/Instagram Reels-style app for learning Calculus 1ZB3 at McMaster University through short, engaging video content.

## Features

- 📱 Vertical scroll interface similar to TikTok/Instagram Reels
- 🎓 Calculus 1ZB3 focused content
- 🎬 Video player with play/pause and mute controls
- ⌨️ Keyboard navigation support (Arrow keys)
- 🎨 Difficulty level indicators (Beginner, Intermediate, Advanced)
- 📚 Topic categorization (Limits, Derivatives, Integration, Applications)
- 🎯 Smooth snap scrolling between videos

## Tech Stack

- **Next.js 16** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React** - UI components

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Barzin-Vazifedoost/CalculusReels.git
cd CalculusReels
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

- **Scroll** vertically to navigate between different calculus topics
- **Click** on the video to play/pause
- **Click** the speaker icon to toggle sound
- Use **Arrow Keys** (↑/↓) to navigate between reels
- Click on the **dots** on the right side to jump to specific videos

## Project Structure

```
CalculusReels/
├── app/
│   ├── data/
│   │   └── calculusReels.ts    # Video data and types
│   ├── globals.css             # Global styles
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Main page with reel container
├── components/
│   └── ReelCard.tsx            # Individual reel component
├── public/                     # Static assets
└── ...config files
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Customization

### Adding New Videos

Edit `app/data/calculusReels.ts` to add new calculus videos:

```typescript
{
  id: 9,
  title: "Your Topic",
  topic: "Topic Category",
  description: "Description of the concept",
  videoUrl: "path/to/video.mp4",
  thumbnail: "path/to/thumbnail.jpg",
  duration: "3:00",
  difficulty: 'beginner' | 'intermediate' | 'advanced'
}
```

## License

ISC

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
