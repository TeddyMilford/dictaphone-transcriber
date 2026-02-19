# Dictaphone Auto-Transcriber

Automatically transcribe voice recordings from dictaphones using Whisper AI with Voice Activity Detection (VAD). Simply plug in your device and transcriptions are created automatically - optimized for AI summarization with Claude or other LLMs.

## Quick Start (Any Dictaphone)

If you don't have a WS-852 dictaphone, you can still use this tool:

1. Clone the repository and install dependencies (see Installation section)
2. Find your device's mount point: `ls /Volumes/`
3. Update `VOLUME_NAME` in `transcribe.py` to match your device name
4. Update the device path in the RECORDER search location if needed
5. Run manually: `python transcribe.py`

The script will find and transcribe all audio files on your device.

## Features

- Automatic transcription when you plug in your dictaphone
- Voice Activity Detection - skips silent parts for 5-10x faster processing
- Batch processing - transcribes all audio files on the device
- AI-optimized output - markdown format with context headers for zero-shot AI summarization
- Desktop output - saves to `~/Desktop/Transcriptions/MM-DD-YYYY.md`
- macOS notifications - alerts you when transcription is complete
- Detailed statistics - shows speech vs silence breakdown

## Prerequisites

- macOS (for LaunchAgent auto-run functionality)
- Python 3.8 or higher
- WS-852 dictaphone (or any USB audio recorder - see Quick Start)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/TeddyMilford/dictaphone-transcriber.git
cd dictaphone-transcriber
```

### 2. Set up Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install faster-whisper

The tool uses faster-whisper for efficient transcription. Install it with:

```bash
pip install -r requirements.txt
```

**Note:** faster-whisper will automatically download the required Whisper model on first run. The "base" model (default) is about 140MB. For more details on faster-whisper, see the [official documentation](https://github.com/SYSTRAN/faster-whisper).

**System Requirements:**
- On macOS Apple Silicon (M1/M2/M3), it will use optimized CPU inference
- First transcription will download the model (one-time, automatic)
- Subsequent runs will use the cached model

### 4. Configure for your device

Edit `transcribe.py` if needed:

```python
VOLUME_NAME = "WS-852"  # Change to your device name from ls /Volumes/
```

### 5. Test manual transcription

```bash
# Plug in your dictaphone first
python transcribe.py
```

Check `~/Desktop/Transcriptions/` for the output file.

### 6. Set up automatic transcription (optional)

**Update the auto-run script path:**

Edit `auto_transcribe.sh` and change this line to your installation path:
```bash
cd "/Users/teddymilford/script_factory/dictaphone_transcriber"
```

**Make it executable:**
```bash
chmod +x auto_transcribe.sh
```

**Create the LaunchAgent plist:**

Create file at `~/Library/LaunchAgents/com.dictaphone.transcriber.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dictaphone.transcriber</string>
    <key>ProgramArguments</key>
    <array>
        <string>/FULL/PATH/TO/YOUR/dictaphone-transcriber/auto_transcribe.sh</string>
    </array>
    <key>WatchPaths</key>
    <array>
        <string>/Volumes/WS-852</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/dictaphone-transcriber.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/dictaphone-transcriber-error.log</string>
</dict>
</plist>
```

**Important:** Replace `/FULL/PATH/TO/YOUR/` with your actual installation path and update `WS-852` to match your device name.

**Load the LaunchAgent:**
```bash
launchctl load ~/Library/LaunchAgents/com.dictaphone.transcriber.plist
```

**Verify:**
```bash
launchctl list | grep dictaphone
```

## Usage

### Automatic Mode
Plug in your dictaphone - transcription starts automatically.
- Runs in background
- macOS notification when complete
- Output: `~/Desktop/Transcriptions/MM-DD-YYYY.md`
- Logs: `~/Desktop/Transcriptions/auto_transcribe.log`

### Manual Mode
```bash
cd /path/to/dictaphone-transcriber
source venv/bin/activate
python transcribe.py
```

## Output Format

Transcriptions are saved as markdown files optimized for AI processing. Each file includes:

**AI Context Header**
- Instructions for AI summarization
- Session metadata (date, duration, speech content percentage)
- Language detection

**Per-Recording Details**
- Filename and recording number
- Duration statistics (total, speech, silence skipped)
- Timestamped transcript segments

**Example structure:**
```markdown
# VOICE RECORDING TRANSCRIPTION

## CONTEXT FOR AI ANALYSIS
This document contains automatic transcriptions from voice recordings...

## INSTRUCTIONS FOR AI SUMMARIZATION
When processing this document:
- Extract key points, action items, and important information
- Identify topics, themes, and categories
...

## SESSION METADATA
- Transcription Date: 2026-02-19
- Total Recordings: 3 files
- Total Audio Duration: 45.2 minutes
- Actual Speech Content: 12.3 minutes (27% of total)
...

## Recording 1: 260220_0065.MP3
Recording Metadata:
- Total Duration: 300.5s (5.0 minutes)
- Speech Duration: 85.2s (1.4 minutes)
...

Transcript:
[0.00s -> 5.23s] First segment of speech...
[5.50s -> 12.80s] Second segment of speech...
```

Simply drag and drop the .md file into Claude or your AI assistant for instant summarization.

## Configuration

Edit `transcribe.py` to customize:

```python
# Model size - balance between speed and accuracy
MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large

# VAD settings - adjust silence detection
VAD_MIN_SILENCE_DURATION_MS = 2000  # Skip silences longer than 2 seconds
VAD_THRESHOLD = 0.5  # Speech detection sensitivity (0-1)

# Device volume name
VOLUME_NAME = "WS-852"

# Output directory
OUTPUT_DIR = Path.home() / "Desktop" / "Transcriptions"
```

**Model Size Guide:**
- tiny: Fastest, least accurate
- base: Default - good balance (recommended)
- small/medium: Better accuracy, slower
- large: Best accuracy, slowest

## Maintenance

**Check auto-run status:**
```bash
launchctl list | grep dictaphone
```

**Disable auto-run:**
```bash
launchctl unload ~/Library/LaunchAgents/com.dictaphone.transcriber.plist
```

**Enable auto-run:**
```bash
launchctl load ~/Library/LaunchAgents/com.dictaphone.transcriber.plist
```

**View logs:**
```bash
# Application log
cat ~/Desktop/Transcriptions/auto_transcribe.log

# System logs
cat /tmp/dictaphone-transcriber.log
cat /tmp/dictaphone-transcriber-error.log
```

## How It Works

1. When device is mounted at `/Volumes/WS-852`, macOS triggers the LaunchAgent
2. `auto_transcribe.sh` activates the Python virtual environment
3. Script finds all audio files in the RECORDER folder (sorted chronologically)
4. Uses faster-whisper with VAD to transcribe, skipping silences
5. Combines all transcriptions into one markdown file with AI-friendly formatting
6. Saves to Desktop/Transcriptions with filename `MM-DD-YYYY.md`
7. Displays macOS notification when complete

## Troubleshooting

**No automatic transcription?**
- Verify volume name: `ls /Volumes/` (should show your device name)
- Check LaunchAgent is loaded: `launchctl list | grep dictaphone`
- Review error logs: `cat /tmp/dictaphone-transcriber-error.log`

**Permission errors?**
- Ensure script is executable: `chmod +x auto_transcribe.sh`
- Check paths in plist file match your installation

**Slow transcription?**
- Try smaller model size: `MODEL_SIZE = "tiny"` or `"base"`
- Increase VAD silence threshold to skip more content

**Want different device?**
- Change `VOLUME_NAME` in `transcribe.py`
- Update WatchPaths in LaunchAgent plist
- Verify device mounts at `/Volumes/` with `ls /Volumes/`

**Model download issues?**
- Ensure internet connection on first run
- Models are cached in `~/.cache/huggingface/`
- See [faster-whisper documentation](https://github.com/SYSTRAN/faster-whisper) for advanced setup

## Tech Stack

- faster-whisper: Optimized Whisper implementation (CTranslate2)
- Voice Activity Detection: Silero VAD for intelligent silence skipping
- macOS LaunchAgent: Automatic device detection and script triggering
- Python 3: Core transcription logic

## License

MIT License - feel free to modify and adapt for your needs.

## Contributing

Issues and pull requests welcome. This was built for personal use but happy to improve it for others.

## Acknowledgments

- OpenAI Whisper for the speech recognition model
- faster-whisper team for the optimized implementation
- Silero VAD for voice activity detection
