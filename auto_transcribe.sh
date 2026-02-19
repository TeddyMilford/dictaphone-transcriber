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
LOG_FILE="$HOME/Desktop/Transcriptions/auto_scribe.log"
mkdir -p "$HOME/Desktop/Transcriptions"

# Log the start
echo "=====================================" >> "$LOG_FILE"
echo "Auto-transcription started: $(date)" >> "$LOG_FILE"
echo "=====================================" >> "$LOG_FILE"

# Run the transcription using the venv python directly
SCRIPT_DIR="/Users/teddymilford/script_factory/dictaphone_transcriber"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
cd "$SCRIPT_DIR"
$VENV_PYTHON transcribe.py >> "$LOG_FILE" 2>&1

# Run summarization and email (only if .env is configured)
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "Starting summarization and email..." >> "$LOG_FILE"
    $VENV_PYTHON summarize_and_email.py >> "$LOG_FILE" 2>&1
else
    echo "Skipping summary/email: .env not configured" >> "$LOG_FILE"
fi

# Log completion
echo "Completed: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Optional: Show a notification when done (requires terminal-notifier or osascript)
osascript -e 'display notification "Transcription complete! Check Desktop/Transcriptions folder." with title "Dictaphone Transcriber"'
