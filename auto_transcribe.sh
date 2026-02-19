#!/bin/bash
# Auto-transcribe script that runs when WS-852 is plugged in

# Wait a moment for the volume to fully mount
sleep 5

# Check if the volume is mounted
if [ ! -d "/Volumes/WS-852" ]; then
    echo "WS-852 volume not found"
    exit 1
fi

SCRIPT_DIR="/Users/teddymilford/script_factory/dictaphone_transcriber"
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python3"

# Log file in ~/Library/Logs (always accessible to LaunchAgents)
LOG_FILE="$HOME/Library/Logs/auto_scribe.log"
mkdir -p "$HOME/Library/Logs"
mkdir -p "$HOME/Documents/Transcriptions"

# Log the start
echo "=====================================" >> "$LOG_FILE"
echo "Auto-transcription started: $(date)" >> "$LOG_FILE"
echo "=====================================" >> "$LOG_FILE"

# Open a Terminal window tailing the log for live progress
osascript -e "tell application \"Terminal\" to do script \"tail -f '$LOG_FILE'\""

# Verify the venv python is functional; rebuild if not
if ! "$VENV_PYTHON" -c "import sys" > /dev/null 2>&1; then
    echo "Venv broken or missing — rebuilding..." >> "$LOG_FILE"
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create venv" >> "$LOG_FILE"
        exit 1
    fi
    echo "Venv created." >> "$LOG_FILE"
fi

# Ensure all requirements are installed
echo "Checking requirements..." >> "$LOG_FILE"
"$VENV_PYTHON" -m pip install -q -r "$SCRIPT_DIR/requirements.txt" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements" >> "$LOG_FILE"
    exit 1
fi

# Run the transcription
"$VENV_PYTHON" "$SCRIPT_DIR/transcribe.py" >> "$LOG_FILE" 2>&1
TRANSCRIBE_EXIT=$?

if [ $TRANSCRIBE_EXIT -ne 0 ]; then
    echo "Error: Transcription failed (exit $TRANSCRIBE_EXIT)" >> "$LOG_FILE"
    echo "Completed with errors: $(date)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    osascript -e 'display notification "Transcription failed. Check ~/Library/Logs/auto_scribe.log for details." with title "Dictaphone Transcriber"'
    exit 1
fi

# Run summarization and email (only if .env is configured)
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "Starting summarization and email..." >> "$LOG_FILE"
    "$VENV_PYTHON" "$SCRIPT_DIR/summarize_and_email.py" >> "$LOG_FILE" 2>&1
    EMAIL_EXIT=$?
    if [ $EMAIL_EXIT -ne 0 ]; then
        echo "Error: Summarization/email failed (exit $EMAIL_EXIT)" >> "$LOG_FILE"
        echo "Completed with errors: $(date)" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        osascript -e 'display notification "Transcription done but email failed. Check ~/Library/Logs/auto_scribe.log." with title "Dictaphone Transcriber"'
        exit 1
    fi
else
    echo "Skipping summary/email: .env not configured" >> "$LOG_FILE"
fi

# Log completion
echo "Completed: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

osascript -e 'display notification "Transcription complete! Check Documents/Transcriptions folder." with title "Dictaphone Transcriber"'
