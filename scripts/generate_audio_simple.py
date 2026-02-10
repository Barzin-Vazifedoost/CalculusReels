"""
Simple audio generation using macOS built-in 'say' command as fallback.
This creates audio files for immediate testing while you set up Google Cloud TTS.
"""

import os
import subprocess
import argparse

# Educational content for each calculus topic (shortened for say command)
TOPICS = [
    (1, "Introduction to Limits", "Limits are the foundation of calculus. A limit describes the value that a function approaches as the input approaches some value."),
    (2, "Derivative Rules", "Derivatives measure the rate of change of a function. The power rule states that the derivative of x to the n equals n times x to the n minus 1."),
    (3, "Chain Rule Explained", "The chain rule is used to find the derivative of composite functions. If we have a function g inside another function f, the derivative involves both functions."),
    (4, "Integration Basics", "Integration is the reverse process of differentiation. The integral of a function represents the area under its curve."),
    (5, "U-Substitution Method", "U-substitution is a technique for solving complex integrals by making a substitution to simplify the integrand."),
    (6, "L'Hopital's Rule", "L'Hopital's rule helps us evaluate limits that give indeterminate forms like 0 over 0 or infinity over infinity."),
    (7, "Implicit Differentiation", "Implicit differentiation is used when we cannot easily solve for y in terms of x."),
    (8, "Related Rates", "Related rates problems involve finding how fast one quantity changes based on how fast related quantities change."),
    (9, "Optimization Problems", "Optimization uses calculus to find maximum and minimum values of functions."),
    (10, "Integration by Parts", "Integration by parts is based on the product rule for derivatives."),
    (11, "Trigonometric Integration", "Integrating trigonometric functions requires special techniques and identities."),
    (12, "Partial Fractions", "Partial fraction decomposition breaks complex rational functions into simpler fractions that are easier to integrate."),
    (13, "Area Between Curves", "To find the area between two curves, we integrate the absolute value of their difference."),
    (14, "Volume by Cross Sections", "We can find volumes by integrating cross-sectional areas."),
    (15, "Arc Length and Surface Area", "The arc length of a curve involves integrating the square root of 1 plus the derivative squared."),
    (16, "Sequences and Series", "A sequence is an ordered list of numbers, while a series is the sum of a sequence's terms."),
    (17, "Taylor and Maclaurin Series", "Taylor series represent functions as infinite polynomials around a point."),
    (18, "Parametric Equations", "Parametric equations express x and y coordinates as functions of a parameter t."),
    (19, "Polar Coordinates", "Polar coordinates express points using radius r and angle theta instead of x and y."),
    (20, "Vector Calculus Intro", "Vector calculus extends single-variable calculus to vector fields and multivariable functions.")
]

def generate_audio_with_say(topic_id, title, content):
    """Generate audio using macOS 'say' command"""
    try:
        output_dir = "../public/audio"
        os.makedirs(output_dir, exist_ok=True)
        
        audio_path = f"{output_dir}/reel-{topic_id}.mp3"
        
        # Use macOS say command with a nice voice
        full_content = f"{title}. {content}"
        
        print(f"🎵 Generating audio for: {title}")
        
        # Use say command to generate audio
        # -o flag saves to file, -v sets voice (Alex is clear for educational content)
        result = subprocess.run([
            "say", 
            "-v", "Alex",
            "-o", audio_path.replace('.mp3', '.aiff'),  # say outputs AIFF
            full_content
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Say command failed: {result.stderr}")
            return False
        
        # Convert AIFF to MP3 using ffmpeg if available, otherwise keep AIFF
        aiff_path = audio_path.replace('.mp3', '.aiff')
        try:
            subprocess.run([
                "ffmpeg", "-i", aiff_path, "-acodec", "mp3", "-y", audio_path
            ], capture_output=True, check=True)
            os.remove(aiff_path)  # Remove AIFF after converting
            print(f"✅ Generated: {audio_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # If ffmpeg is not available, rename AIFF to MP3 extension
            mp3_path = audio_path
            os.rename(aiff_path, mp3_path)
            print(f"✅ Generated: {mp3_path} (AIFF format)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating audio for {title}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate calculus audio content using macOS say command")
    parser.add_argument("--force", action="store_true", help="Regenerate all audio files")
    parser.add_argument("--id", type=int, help="Generate audio for specific topic ID only")
    args = parser.parse_args()
    
    # Check if we're on macOS
    if os.system("which say > /dev/null 2>&1") != 0:
        print("❌ This script requires macOS 'say' command")
        print("💡 Use generate_audio_gcp.py for cross-platform Google Cloud TTS")
        return
    
    # Filter topics based on arguments
    topics_to_process = TOPICS
    if args.id:
        topics_to_process = [(id, title, content) for id, title, content in TOPICS if id == args.id]
        if not topics_to_process:
            print(f"❌ Topic ID {args.id} not found")
            return
    
    print(f"🎯 Generating audio for {len(topics_to_process)} topic(s) using macOS say...")
    
    success_count = 0
    for topic_id, title, content in topics_to_process:
        # Check if file already exists (unless force flag is set)
        output_path = f"../public/audio/reel-{topic_id}.mp3"
        if not args.force and os.path.exists(output_path):
            print(f"⏭️  Skipping {title} (already exists)")
            success_count += 1
            continue
            
        if generate_audio_with_say(topic_id, title, content):
            success_count += 1
    
    print(f"\n🎉 Successfully generated {success_count} audio files!")
    print("🚀 Your CalculusReels app is now ready with audio content!")

if __name__ == "__main__":
    main()