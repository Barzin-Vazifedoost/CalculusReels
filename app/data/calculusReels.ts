export interface CalculusReel {
  id: number;
  title: string;
  topic: string;
  description: string;
  audioUrl: string;
  videoUrl?: string;
  sourceVideoUrl: string;
  duration: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  color: string;
  icon: string;
}

export const topicColors: Record<string, string> = {
  Limits: '#3B82F6',
  Derivatives: '#8B5CF6',
  Integration: '#10B981',
  Applications: '#F59E0B',
  Series: '#EF4444',
  Theorems: '#EC4899',
};

export const topicIcons: Record<string, string> = {
  Limits: 'lim',
  Derivatives: "f'",
  Integration: '\u222B',
  Applications: '\u0394',
  Series: '\u03A3',
  Theorems: '\u2234',
};

export const allCalculusReels: CalculusReel[] = [
  {
    id: 1,
    title: 'Introduction to Limits',
    topic: 'Limits',
    description: 'Understanding the basic concept of limits and how to evaluate them',
    audioUrl: '/audio/reel-1.mp3',
    videoUrl: '/videos/reel-1.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=riXcZT2ICjA',
    duration: '12:14',
    difficulty: 'beginner',
    color: '#3B82F6',
    icon: 'lim',
  },
  {
    id: 2,
    title: 'Derivative Rules',
    topic: 'Derivatives',
    description: 'Learn the power rule, product rule, and quotient rule for derivatives',
    audioUrl: '/audio/reel-2.mp3',
    videoUrl: '/videos/reel-2.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=S2_noq_VIcE',
    duration: '11:35',
    difficulty: 'intermediate',
    color: '#8B5CF6',
    icon: "f'",
  },
  {
    id: 3,
    title: 'Chain Rule Explained',
    topic: 'Derivatives',
    description: 'Master the chain rule for composite functions',
    audioUrl: '/audio/reel-3.mp3',
    videoUrl: '/videos/reel-3.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=H-ybCx8gt-8',
    duration: '9:42',
    difficulty: 'intermediate',
    color: '#8B5CF6',
    icon: "f'",
  },
  {
    id: 4,
    title: 'Integration Basics',
    topic: 'Integration',
    description: 'Introduction to indefinite and definite integrals',
    audioUrl: '/audio/reel-4.mp3',
    videoUrl: '/videos/reel-4.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=rfG8ce4nNh0',
    duration: '18:43',
    difficulty: 'beginner',
    color: '#10B981',
    icon: '\u222B',
  },
  {
    id: 5,
    title: 'U-Substitution Method',
    topic: 'Integration',
    description: 'Learn how to solve integrals using u-substitution',
    audioUrl: '/audio/reel-5.mp3',
    videoUrl: '/videos/reel-5.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=o3Zz97_-j5c',
    duration: '14:28',
    difficulty: 'intermediate',
    color: '#10B981',
    icon: '\u222B',
  },
  {
    id: 6,
    title: "L'H\u00F4pital's Rule",
    topic: 'Limits',
    description: "Using L'H\u00F4pital's rule for indeterminate forms",
    audioUrl: '/audio/reel-6.mp3',
    videoUrl: '/videos/reel-6.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=kfF40MiS7zA',
    duration: '16:25',
    difficulty: 'advanced',
    color: '#3B82F6',
    icon: 'lim',
  },
  {
    id: 7,
    title: 'Implicit Differentiation',
    topic: 'Derivatives',
    description: "Differentiate equations that aren't explicitly solved for y",
    audioUrl: '/audio/reel-7.mp3',
    videoUrl: '/videos/reel-7.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=qb40J4N1fa4',
    duration: '13:07',
    difficulty: 'advanced',
    color: '#8B5CF6',
    icon: "f'",
  },
  {
    id: 8,
    title: 'Related Rates',
    topic: 'Applications',
    description: 'Solve real-world problems with related rates',
    audioUrl: '/audio/reel-8.mp3',
    videoUrl: '/videos/reel-8.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=CyfpNz85T6w',
    duration: '15:33',
    difficulty: 'advanced',
    color: '#F59E0B',
    icon: '\u0394',
  },
  {
    id: 9,
    title: 'Fundamental Theorem of Calculus',
    topic: 'Integration',
    description: 'Understanding the connection between derivatives and integrals',
    audioUrl: '/audio/reel-9.mp3',
    videoUrl: '/videos/reel-9.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=HfACrKJ_Y2w',
    duration: '19:24',
    difficulty: 'intermediate',
    color: '#10B981',
    icon: '\u222B',
  },
  {
    id: 10,
    title: 'Integration by Parts',
    topic: 'Integration',
    description: 'Master the integration by parts technique',
    audioUrl: '/audio/reel-10.mp3',
    videoUrl: '/videos/reel-10.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=2I-_SV8cwsw',
    duration: '17:15',
    difficulty: 'advanced',
    color: '#10B981',
    icon: '\u222B',
  },
  {
    id: 11,
    title: 'Optimization Problems',
    topic: 'Applications',
    description: 'Find maximum and minimum values in real-world scenarios',
    audioUrl: '/audio/reel-11.mp3',
    videoUrl: '/videos/reel-11.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=WUvTyaaNkzM',
    duration: '22:18',
    difficulty: 'advanced',
    color: '#F59E0B',
    icon: '\u0394',
  },
  {
    id: 12,
    title: 'Mean Value Theorem',
    topic: 'Theorems',
    description: 'Understanding and applying the mean value theorem',
    audioUrl: '/audio/reel-12.mp3',
    videoUrl: '/videos/reel-12.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=SJe21zF5xNM',
    duration: '14:52',
    difficulty: 'intermediate',
    color: '#EC4899',
    icon: '\u2234',
  },
  {
    id: 13,
    title: 'Partial Fractions',
    topic: 'Integration',
    description: 'Decompose rational functions for easier integration',
    audioUrl: '/audio/reel-13.mp3',
    videoUrl: '/videos/reel-13.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=YQW_adN0jKw',
    duration: '26:33',
    difficulty: 'advanced',
    color: '#10B981',
    icon: '\u222B',
  },
  {
    id: 14,
    title: 'Trigonometric Substitution',
    topic: 'Integration',
    description: 'Use trig substitution for complex integrals',
    audioUrl: '/audio/reel-14.mp3',
    videoUrl: '/videos/reel-14.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=8GPkwvZcGvs',
    duration: '23:47',
    difficulty: 'advanced',
    color: '#10B981',
    icon: '\u222B',
  },
  {
    id: 15,
    title: 'Infinite Series Introduction',
    topic: 'Series',
    description: 'Basic concepts of infinite series and convergence',
    audioUrl: '/audio/reel-15.mp3',
    videoUrl: '/videos/reel-15.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=Tj8p_mpICa8',
    duration: '20:15',
    difficulty: 'advanced',
    color: '#EF4444',
    icon: '\u03A3',
  },
  {
    id: 16,
    title: "Newton's Method",
    topic: 'Applications',
    description: "Approximate roots using Newton's iterative method",
    audioUrl: '/audio/reel-16.mp3',
    videoUrl: '/videos/reel-16.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=1uN8cBGVpfs',
    duration: '16:28',
    difficulty: 'intermediate',
    color: '#F59E0B',
    icon: '\u0394',
  },
  {
    id: 17,
    title: 'Parametric Equations',
    topic: 'Applications',
    description: 'Work with curves defined parametrically',
    audioUrl: '/audio/reel-17.mp3',
    videoUrl: '/videos/reel-17.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=GNcFjFmqEc8',
    duration: '18:35',
    difficulty: 'intermediate',
    color: '#F59E0B',
    icon: '\u0394',
  },
  {
    id: 18,
    title: 'Area Between Curves',
    topic: 'Integration',
    description: 'Calculate areas between two or more curves',
    audioUrl: '/audio/reel-18.mp3',
    videoUrl: '/videos/reel-18.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=x_TkJcMZm6s',
    duration: '21:42',
    difficulty: 'intermediate',
    color: '#10B981',
    icon: '\u222B',
  },
  {
    id: 19,
    title: 'Improper Integrals',
    topic: 'Integration',
    description: 'Handle integrals with infinite bounds or discontinuities',
    audioUrl: '/audio/reel-19.mp3',
    videoUrl: '/videos/reel-19.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=fWOGfzC3IeY',
    duration: '19:16',
    difficulty: 'advanced',
    color: '#10B981',
    icon: '\u222B',
  },
  {
    id: 20,
    title: 'Taylor Series',
    topic: 'Series',
    description: 'Represent functions as infinite polynomials',
    audioUrl: '/audio/reel-20.mp3',
    videoUrl: '/videos/reel-20.mp4',
    sourceVideoUrl: 'https://www.youtube.com/watch?v=3d6DsjIBzJ4',
    duration: '25:18',
    difficulty: 'advanced',
    color: '#EF4444',
    icon: '\u03A3',
  },
];

function fisherYatesShuffle<T>(arr: T[]): T[] {
  const shuffled = [...arr];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export function getRandomVideoSet(count: number = 8): CalculusReel[] {
  return fisherYatesShuffle(allCalculusReels).slice(0, count);
}

export function getVideosByDifficulty(
  difficulty: 'beginner' | 'intermediate' | 'advanced',
  count: number = 8
): CalculusReel[] {
  const filtered = allCalculusReels.filter((reel) => reel.difficulty === difficulty);
  return fisherYatesShuffle(filtered).slice(0, Math.min(count, filtered.length));
}

export function getVideosByTopic(topic: string, count: number = 8): CalculusReel[] {
  const filtered = allCalculusReels.filter(
    (reel) => reel.topic.toLowerCase() === topic.toLowerCase()
  );
  return fisherYatesShuffle(filtered).slice(0, Math.min(count, filtered.length));
}
