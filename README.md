# Dictaphone Auto-Transcriber

Automatically transcribe voice recordings from your WS-852 dictaphone using Whisper AI with Voice Activity Detection (VAD). Simply plug in your device and transcriptions are created automatically - optimized for AI summarization with Claude or other LLMs.

## Features

- ✅ **Automatic transcription** when you plug in your WS-852 dictaphone
- ✅ **Voice Activity Detection** - skips silent parts for 5-10x faster processing
- ✅ **Batch processing** - transcribes all audio files on the device
- ✅ **AI-optimized output** - markdown format with context headers for zero-shot AI summarization
- ✅ **Desktop output** - saves to `~/Desktop/Transcriptions/MM-DD-YYYY.md`
- ✅ **macOS notifications** - alerts you when transcription is complete
- ✅ **Detailed statistics** - shows speech vs silence breakdown

## Installation

### Prerequisites
- macOS (for LaunchAgent auto-run functionality)
- Python 3.8+
- WS-852 dictaphone (or modify `VOLUME_NAME` in script for other devices)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TeddyMilford/dictaphone-transcriber.git
   cd dictaphone-transcriber
   ```

2. **Create virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Update paths in configuration files:**
   
   Edit `auto_transcribe.sh` and update the path to match your installation:
   ```bash
   cd "/path/to/your/dictaphone-transcriber"
   ```

4. **Make the auto-run script executable:**
   ```bash
   chmod +x auto_transcribe.sh
   ```

5. **Install the LaunchAgent (for automatic transcription):**
   
   Create the plist file at `~/Library/LaunchAgents/com.dictaphone.transcriber.plist`:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.dictaphone.transcriber</string>
       <key>ProgramArguments</key>
       <array>
           <string>/path/to/your/dictaphone-transcriber/auto_transcribe.sh</string>
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

6. **Load the LaunchAgent:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.dictaphone.transcriber.plist
   ```

7. **Verify it's running:**
   ```bash
   launchctl list | grep dictaphone
   ```

## Usage

### Automatic Mode (Recommended)
Simply plug in your WS-852 dictaphone and the transcription starts automatically!

- Transcription runs in the background
- macOS notification appears when complete
- Output saved to `~/Desktop/Transcriptions/MM-DD-YYYY.md`
- Check logs at `~/Desktop/Transcriptions/auto_transcribe.log`

### Manual Mode
You can also run transcriptions manually:
```bash
cd /path/to/dictaphone-transcriber
source venv/bin/activate
python transcribe.py
```

## Output Format

Transcriptions are saved as markdown files optimized for AI processing. Each file includes:

### AI Context Header
- Clear instructions for AI summarization
- Session metadata (date, duration, speech content %)
- Language detection

### Per-Recording Details
- Filename and recording number
- Duration statistics (total, speech, silence skipped)
- Timestamped transcript segments

### Example Output Structure:
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
- **Transcription Date**: 2026-02-19
- **Total Recordings**: 3 file(s)
- **Total Audio Duration**: 45.2 minutes
- **Actual Speech Content**: 12.3 minutes (27.2% of total)
...

## Recording 1: 260220_0065.MP3
**Recording Metadata:**
- Total Duration: 300.5s (5.0 minutes)
- Speech Duration: 85.2s (1.4 minutes)
...

**Transcript:**
[0.00s -> 5.23s] First segment of speech...
[5.50s -> 12.80s] Second segment of speech...
```

Simply drag and drop the `.md` file into Claude or your preferred AI assistant for instant summarization!

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

### Model Size Guide:
- **tiny**: Fastest, least accurate
- **base**: Default - good balance
- **small/medium**: Better accuracy, slower
- **large**: Best accuracy, slowest

## Maintenance

### Check auto-run status:
```bash
launchctl list | grep dictaphone
```

### Disable auto-run:
```bash
launchctl unload ~/Library/LaunchAgents/com.dictaphone.transcriber.plist
```

### Enable auto-run:
```bash
launchctl load ~/Library/LaunchAgents/com.dictaphone.transcriber.plist
```

### View logs:
```bash
# Application log
cat ~/Desktop/Transcriptions/auto_transcribe.log

# System logs
cat /tmp/dictaphone-transcriber.log
cat /tmp/dictaphone-transcriber-error.log
```

## How It Works

1. When WS-852 is mounted at `/Volumes/WS-852`, macOS triggers the LaunchAgent
2. `auto_transcribe.sh` activates the Python virtual environment
3. Script finds all audio files in the RECORDER folder (sorted chronologically)
4. Uses faster-whisper with VAD to transcribe, skipping silences
5. Combines all transcriptions into one markdown file with AI-friendly formatting
6. Saves to Desktop/Transcriptions with filename `MM-DD-YYYY.md`
7. Displays macOS notification when complete

## Troubleshooting

**No automatic transcription?**
- Verify volume name: `ls /Volumes/` (should show WS-852)
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

## Tech Stack

- **faster-whisper**: Optimized Whisper implementation (CTranslate2)
- **Voice Activity Detection**: Silero VAD for intelligent silence skipping
- **macOS LaunchAgent**: Automatic device detection and script triggering
- **Python 3**: Core transcription logic

## License

MIT License - feel free to modify and adapt for your needs!

## Contributing

Issues and pull requests welcome! This was built for personal use but happy to improve it for others.

## Acknowledgments

- OpenAI Whisper for the incredible speech recognition model
- faster-whisper team for the optimized implementation
- Silero VAD for voice activity detection
