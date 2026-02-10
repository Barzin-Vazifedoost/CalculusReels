export interface CalculusReel {
  id: number;
  title: string;
  topic: string;
  description: string;
  videoUrl: string;
  thumbnail: string;
  duration: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

export const calculusReels: CalculusReel[] = [
  {
    id: 1,
    title: "Introduction to Limits",
    topic: "Limits",
    description: "Understanding the basic concept of limits and how to evaluate them",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    thumbnail: "https://via.placeholder.com/400x600/4F46E5/FFFFFF?text=Limits",
    duration: "2:30",
    difficulty: 'beginner'
  },
  {
    id: 2,
    title: "Derivative Rules",
    topic: "Derivatives",
    description: "Learn the power rule, product rule, and quotient rule for derivatives",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    thumbnail: "https://via.placeholder.com/400x600/7C3AED/FFFFFF?text=Derivatives",
    duration: "3:15",
    difficulty: 'intermediate'
  },
  {
    id: 3,
    title: "Chain Rule Explained",
    topic: "Derivatives",
    description: "Master the chain rule for composite functions",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    thumbnail: "https://via.placeholder.com/400x600/EC4899/FFFFFF?text=Chain+Rule",
    duration: "2:45",
    difficulty: 'intermediate'
  },
  {
    id: 4,
    title: "Integration Basics",
    topic: "Integration",
    description: "Introduction to indefinite and definite integrals",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    thumbnail: "https://via.placeholder.com/400x600/10B981/FFFFFF?text=Integration",
    duration: "4:00",
    difficulty: 'beginner'
  },
  {
    id: 5,
    title: "U-Substitution Method",
    topic: "Integration",
    description: "Learn how to solve integrals using u-substitution",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
    thumbnail: "https://via.placeholder.com/400x600/F59E0B/FFFFFF?text=U-Sub",
    duration: "3:30",
    difficulty: 'intermediate'
  },
  {
    id: 6,
    title: "L'Hôpital's Rule",
    topic: "Limits",
    description: "Using L'Hôpital's rule for indeterminate forms",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
    thumbnail: "https://via.placeholder.com/400x600/EF4444/FFFFFF?text=L'Hopital",
    duration: "2:50",
    difficulty: 'advanced'
  },
  {
    id: 7,
    title: "Implicit Differentiation",
    topic: "Derivatives",
    description: "Differentiate equations that aren't explicitly solved for y",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
    thumbnail: "https://via.placeholder.com/400x600/3B82F6/FFFFFF?text=Implicit+Diff",
    duration: "3:20",
    difficulty: 'advanced'
  },
  {
    id: 8,
    title: "Related Rates",
    topic: "Applications",
    description: "Solve real-world problems with related rates",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    thumbnail: "https://via.placeholder.com/400x600/8B5CF6/FFFFFF?text=Related+Rates",
    duration: "4:15",
    difficulty: 'advanced'
  }
];
