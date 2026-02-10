# Audio Generation Pipeline

Generates NotebookLM audio overviews for each calculus topic.

## Automated (recommended)

### One-time setup

```bash
cd scripts
pip install -r requirements.txt
playwright install chromium
notebooklm login    # opens browser for Google OAuth
```

### Generate audio

```bash
# Generate all missing audio files
python generate_audio.py

# Regenerate everything from scratch
python generate_audio.py --force

# Regenerate a single topic (by ID, 1-20)
python generate_audio.py --id 5

# Adjust delay between topics (default 30s)
python generate_audio.py --delay 60
```

Audio files are saved to `public/audio/reel-{id}.mp3`.

## Manual fallback

If `notebooklm-py` breaks (it uses unofficial APIs), generate manually:

1. Go to [notebooklm.google.com](https://notebooklm.google.com)
2. Create a new notebook
3. Add the YouTube URL as a source (paste the link)
4. Click **Audio Overview** > **Generate**
5. Wait 2-5 minutes for generation
6. Download the audio file
7. Rename to `reel-{id}.mp3` and place in `public/audio/`

Repeat for each of the 20 topics. See `generate_audio.py` for the full topic list.
