"""
Generate enhanced calculus content using Gemini Flash and convert to audio.
This creates much more engaging, detailed educational content than the simple TTS approach.

Prerequisites:
  pip install -r requirements.txt
  export GEMINI_API_KEY="your-gemini-api-key"

Usage:
  python generate_audio_gemini.py              # generate all missing
  python generate_audio_gemini.py --force      # regenerate everything  
  python generate_audio_gemini.py --id 3       # regenerate a single topic
"""

import os
import sys
import argparse
import subprocess
import google.generativeai as genai
from typing import Dict, List, Tuple
from pathlib import Path

# Load environment variables from .env file
def load_env():
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

load_env()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found")
    print("💡 Add your API key to .env file: GEMINI_API_KEY=your-key-here")
    sys.exit(1)

# Set the API key as environment variable for google.generativeai
os.environ['GOOGLE_API_KEY'] = GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Calculus topics with enhanced metadata
TOPICS = [
    (1, "Introduction to Limits", "Limits", "beginner", 
     "The foundation of calculus - understanding what happens as we approach a value"),
    
    (2, "Derivative Rules", "Derivatives", "beginner",
     "Master the essential rules for finding derivatives of any function"),
    
    (3, "Chain Rule Explained", "Derivatives", "intermediate", 
     "The most powerful differentiation technique for composite functions"),
    
    (4, "Integration Basics", "Integration", "beginner",
     "Understanding integration as the reverse of differentiation and area under curves"),
    
    (5, "U-Substitution Method", "Integration", "intermediate",
     "The key technique for solving complex integrals through substitution"),
    
    (6, "L'Hopital's Rule", "Limits", "advanced",
     "Solving indeterminate forms and tricky limit problems"),
    
    (7, "Implicit Differentiation", "Derivatives", "intermediate",
     "Finding derivatives when you can't solve explicitly for y"),
    
    (8, "Related Rates", "Applications", "intermediate",
     "Connecting rates of change in real-world scenarios"),
    
    (9, "Optimization Problems", "Applications", "advanced",
     "Using calculus to find maximum and minimum values in practical situations"),
    
    (10, "Integration by Parts", "Integration", "advanced",
     "The product rule in reverse - integrating products of functions"),
    
    (11, "Trigonometric Integration", "Integration", "advanced",
     "Special techniques for integrating trigonometric functions"),
    
    (12, "Partial Fractions", "Integration", "advanced",
     "Breaking down complex rational functions for easier integration"),
    
    (13, "Area Between Curves", "Applications", "intermediate",
     "Using integration to find areas between intersecting curves"),
    
    (14, "Volume by Cross Sections", "Applications", "advanced",
     "Finding volumes using the disk, washer, and cross-section methods"),
    
    (15, "Arc Length and Surface Area", "Applications", "advanced",
     "Calculating lengths of curves and areas of surfaces of revolution"),
    
    (16, "Sequences and Series", "Series", "intermediate",
     "Understanding infinite sequences and when their sums converge"),
    
    (17, "Taylor and Maclaurin Series", "Series", "advanced",
     "Representing functions as infinite polynomials"),
    
    (18, "Parametric Equations", "Applications", "intermediate",
     "Describing curves using parameter equations and finding their derivatives"),
    
    (19, "Polar Coordinates", "Applications", "intermediate",
     "Working with curves in polar form and calculating areas and arc lengths"),
    
    (20, "Vector Calculus Intro", "Applications", "advanced",
     "Extending calculus to vector fields and multivariable functions")
]

def generate_educational_content(topic_id: int, title: str, category: str, difficulty: str, description: str) -> str:
    """Generate engaging educational content using Gemini Flash"""
    
    prompt = f"""
Create an engaging, educational audio script about "{title}" for university calculus students. 

Topic Details:
- Title: {title}
- Category: {category}
- Difficulty: {difficulty}
- Description: {description}

Requirements:
- Write in a conversational, engaging tone suitable for audio
- Keep it between 2-3 minutes when spoken (approximately 300-450 words)
- Start with a brief, catchy hook
- Include clear explanations with intuitive examples
- Use concrete analogies when helpful
- End with a practical application or key takeaway
- Avoid complex mathematical notation - describe formulas in words
- Make it accessible but not oversimplified

Focus on building understanding and intuition rather than just memorizing formulas.

Write the script now:
"""
    
    try:
        print(f"🧠 Generating content for: {title}")
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        if not content:
            raise ValueError("Empty response from Gemini")
            
        print(f"✅ Generated {len(content)} characters of content")
        return content
        
    except Exception as e:
        print(f"❌ Error generating content for {title}: {e}")
        # Fallback to simple content
        return f"""
Welcome to {title}. 

This is an important topic in calculus that helps us understand {description.lower()}. 

{title} is classified as a {difficulty} level topic in the {category} category. 
Understanding this concept will help you solve more complex problems and build a strong foundation in calculus.

Let's explore the key concepts and see how they apply to real-world situations.
"""

def text_to_audio(text: str, topic_id: int, title: str) -> bool:
    """Convert text to audio using macOS say command"""
    try:
        output_dir = "../public/audio"
        os.makedirs(output_dir, exist_ok=True)
        
        audio_path = f"{output_dir}/reel-{topic_id}.mp3"
        
        print(f"🎵 Converting to audio: {title}")
        
        # Use macOS say command with a pleasant voice for educational content
        result = subprocess.run([
            "say", 
            "-v", "Alex",  # Clear, professional voice
            "-r", "180",   # Slightly slower speaking rate for education
            "-o", audio_path.replace('.mp3', '.aiff'),
            text
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Say command failed: {result.stderr}")
            return False
        
        # Convert AIFF to MP3 if ffmpeg is available
        aiff_path = audio_path.replace('.mp3', '.aiff')
        try:
            subprocess.run([
                "ffmpeg", "-i", aiff_path, "-acodec", "mp3", "-y", audio_path
            ], capture_output=True, check=True)
            os.remove(aiff_path)
            print(f"✅ Generated MP3: {audio_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Keep AIFF if ffmpeg not available
            os.rename(aiff_path, audio_path)
            print(f"✅ Generated audio: {audio_path} (AIFF format)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting to audio for {title}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate calculus audio content using Gemini Flash + TTS")
    parser.add_argument("--force", action="store_true", help="Regenerate all audio files")
    parser.add_argument("--id", type=int, help="Generate audio for specific topic ID only")
    args = parser.parse_args()
    
    # Check if we're on macOS
    if os.system("which say > /dev/null 2>&1") != 0:
        print("❌ This script requires macOS 'say' command")
        print("💡 Consider using the Google Cloud TTS version instead")
        return
    
    # Filter topics based on arguments
    topics_to_process = TOPICS
    if args.id:
        topics_to_process = [(id, title, cat, diff, desc) for id, title, cat, diff, desc in TOPICS if id == args.id]
        if not topics_to_process:
            print(f"❌ Topic ID {args.id} not found")
            return
    
    print(f"🎯 Generating Gemini-powered content for {len(topics_to_process)} topic(s)...")
    print(f"🤖 Using Gemini Flash model for content generation")
    
    success_count = 0
    for topic_id, title, category, difficulty, description in topics_to_process:
        # Check if file already exists (unless force flag is set)
        output_path = f"../public/audio/reel-{topic_id}.mp3"
        if not args.force and os.path.exists(output_path):
            print(f"⏭️  Skipping {title} (already exists)")
            success_count += 1
            continue
        
        # Generate content with Gemini
        content = generate_educational_content(topic_id, title, category, difficulty, description)
        
        # Convert to audio
        if text_to_audio(content, topic_id, title):
            success_count += 1
        
        print()  # Add spacing between topics
    
    print(f"🎉 Successfully generated {success_count} Gemini-powered audio files!")
    print("🚀 Your CalculusReels app now has AI-enhanced educational content!")

if __name__ == "__main__":
    main()