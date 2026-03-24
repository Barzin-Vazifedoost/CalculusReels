"""
Generate audio overviews for each calculus topic using NotebookLM.

Prerequisites:
  pip install -r requirements.txt
  playwright install chromium
  notebooklm login          # one-time browser OAuth

Usage:
  python generate_audio.py              # generate all missing
  python generate_audio.py --force      # regenerate everything
  python generate_audio.py --id 3       # regenerate a single topic
"""

import os
import sys
import asyncio
import argparse

# Each topic: (id, title, youtube_url)
# These YouTube URLs are fed into NotebookLM to generate AI audio overviews.
TOPICS = [
    (1,  "Introduction to Limits",          "https://www.youtube.com/watch?v=riXcZT2ICjA"),
    (2,  "Derivative Rules",                "https://www.youtube.com/watch?v=S2_noq_VIcE"),
    (3,  "Chain Rule Explained",            "https://www.youtube.com/watch?v=H-ybCx8gt-8"),
    (4,  "Integration Basics",              "https://www.youtube.com/watch?v=rfG8ce4nNh0"),
    (5,  "U-Substitution Method",           "https://www.youtube.com/watch?v=o3Zz97_-j5c"),
    (6,  "L'Hopital's Rule",               "https://www.youtube.com/watch?v=kfF40MiS7zA"),
    (7,  "Implicit Differentiation",        "https://www.youtube.com/watch?v=qb40J4N1fa4"),
    (8,  "Related Rates",                   "https://www.youtube.com/watch?v=CyfpNz85T6w"),
    (9,  "Fundamental Theorem of Calculus",  "https://www.youtube.com/watch?v=HfACrKJ_Y2w"),
    (10, "Integration by Parts",            "https://www.youtube.com/watch?v=2I-_SV8cwsw"),
    (11, "Optimization Problems",           "https://www.youtube.com/watch?v=WUvTyaaNkzM"),
    (12, "Mean Value Theorem",              "https://www.youtube.com/watch?v=SJe21zF5xNM"),
    (13, "Partial Fractions",               "https://www.youtube.com/watch?v=YQW_adN0jKw"),
    (14, "Trigonometric Substitution",      "https://www.youtube.com/watch?v=8GPkwvZcGvs"),
    (15, "Infinite Series Introduction",    "https://www.youtube.com/watch?v=Tj8p_mpICa8"),
    (16, "Newton's Method",                 "https://www.youtube.com/watch?v=1uN8cBGVpfs"),
    (17, "Parametric Equations",            "https://www.youtube.com/watch?v=GNcFjFmqEc8"),
    (18, "Area Between Curves",             "https://www.youtube.com/watch?v=x_TkJcMZm6s"),
    (19, "Improper Integrals",              "https://www.youtube.com/watch?v=fWOGfzC3IeY"),
    (20, "Taylor Series",                   "https://www.youtube.com/watch?v=3d6DsjIBzJ4"),
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "audio")

AUDIO_INSTRUCTIONS = (
    "Create an engaging, educational audio discussion about this calculus topic. "
    "Assume the listener is a university student taking Calculus 1 (Calc 1ZB3 at McMaster). "
    "Keep it concise, clear, and focused on building intuition. "
    "Use examples where helpful."
)


async def generate_one(client, reel_id: int, title: str, url: str) -> bool:
    """Generate audio for a single topic. Returns True on success."""
    output_path = os.path.join(OUTPUT_DIR, f"reel-{reel_id}.mp3")

    try:
        print(f"  [{reel_id}/20] Creating notebook for: {title}")
        nb = await client.notebooks.create(f"CalculusReels - {title}")

        print(f"  [{reel_id}/20] Adding YouTube source...")
        await client.sources.add_url(nb.id, url, wait=True)

        print(f"  [{reel_id}/20] Generating audio overview (this takes a few minutes)...")
        status = await client.artifacts.generate_audio(
            nb.id, instructions=AUDIO_INSTRUCTIONS
        )
        await client.artifacts.wait_for_completion(nb.id, status.task_id)

        print(f"  [{reel_id}/20] Downloading audio...")
        await client.artifacts.download_audio(nb.id, output_path)

        print(f"  [{reel_id}/20] Done -> {output_path}")
        return True

    except Exception as e:
        print(f"  [{reel_id}/20] FAILED: {e}", file=sys.stderr)
        return False


async def main():
    parser = argparse.ArgumentParser(description="Generate NotebookLM audio for CalculusReels")
    parser.add_argument("--force", action="store_true", help="Regenerate all, even if file exists")
    parser.add_argument("--id", type=int, help="Generate only this topic ID")
    parser.add_argument("--delay", type=int, default=30, help="Seconds between topics (rate limit protection)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Filter topics
    topics = TOPICS
    if args.id:
        topics = [(tid, t, u) for tid, t, u in TOPICS if tid == args.id]
        if not topics:
            print(f"No topic with id={args.id}")
            sys.exit(1)

    # Import here so the script shows a helpful error if not installed
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("notebooklm-py is not installed. Run:")
        print("  pip install -r requirements.txt")
        print("  playwright install chromium")
        print("  notebooklm login")
        sys.exit(1)

    print(f"Generating audio for {len(topics)} topic(s)...\n")
    successes, failures = 0, 0

    async with await NotebookLMClient.from_storage() as client:
        for i, (reel_id, title, url) in enumerate(topics):
            output_path = os.path.join(OUTPUT_DIR, f"reel-{reel_id}.mp3")

            if not args.force and os.path.exists(output_path):
                print(f"  [{reel_id}/20] Skipping (already exists): {output_path}")
                successes += 1
                continue

            ok = await generate_one(client, reel_id, title, url)
            if ok:
                successes += 1
            else:
                failures += 1

            # Rate limit protection between topics
            if i < len(topics) - 1:
                print(f"  Waiting {args.delay}s before next topic...")
                await asyncio.sleep(args.delay)

    print(f"\nDone: {successes} succeeded, {failures} failed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
