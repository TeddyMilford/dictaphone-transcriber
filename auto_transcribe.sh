#!/bin/bash
# Auto-transcribe script that runs when WS-852 is plugged in

# Wait a moment for the volume to fully mount
sleep 5

# Check if the volume is mounted
if [ ! -d "/Volumes/WS-852" ]; then
    echo "WS-852 volume not found"
    exit 1
fi

# Log file on Desktop
LOG_FILE="$HOME/Desktop/Transcriptions/auto_transcribe.log"
mkdir -p "$HOME/Desktop/Transcriptions"

# Log the start
echo "=====================================" >> "$LOG_FILE"
echo "Auto-transcription started: $(date)" >> "$LOG_FILE"
echo "=====================================" >> "$LOG_FILE"

# Activate virtual environment and run the transcription
cd "/Users/teddymilford/script_factory/dictaphone_transcriber"
source venv/bin/activate
python transcribe.py >> "$LOG_FILE" 2>&1

# Log completion
echo "Completed: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Optional: Show a notification when done (requires terminal-notifier or osascript)
osascript -e 'display notification "Transcription complete! Check Desktop/Transcriptions folder." with title "Dictaphone Transcriber"'
