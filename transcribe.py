#!/usr/bin/env python3
"""
Transcribe audio files from WS-852 dictaphone using faster-whisper
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from faster_whisper import WhisperModel

# Configuration
VOLUME_NAME = "WS-852"
VOLUME_PATH = f"/Volumes/{VOLUME_NAME}"
OUTPUT_DIR = Path.home() / "Desktop" / "Transcriptions"
MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large

# VAD (Voice Activity Detection) settings
# This will skip silent parts and only transcribe speech
VAD_FILTER = True
VAD_MIN_SILENCE_DURATION_MS = 2000  # Skip silences longer than 2 seconds
VAD_THRESHOLD = 0.5  # Speech detection sensitivity (0-1, higher = more strict)

def find_all_audio_files():
    """Find all audio files on the WS-852 volume"""
    if not os.path.exists(VOLUME_PATH):
        raise FileNotFoundError(f"Volume {VOLUME_NAME} not found at {VOLUME_PATH}")

    audio_extensions = ['.wav', '.mp3', '.m4a', '.wma', '.flac']
    audio_files = []

    # Search in RECORDER folder where the device stores recordings
    recorder_path = os.path.join(VOLUME_PATH, "RECORDER")
    if os.path.exists(recorder_path):
        for root, dirs, files in os.walk(recorder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    full_path = os.path.join(root, file)
                    audio_files.append((full_path, os.path.getmtime(full_path)))

    # Sort by modification time (oldest first)
    audio_files.sort(key=lambda x: x[1])

    # Return just the file paths
    return [f[0] for f in audio_files]

def transcribe_audio(audio_path, model):
    """Transcribe a single audio file with VAD to skip silences"""
    print(f"Transcribing: {os.path.basename(audio_path)}")
    print("Using Voice Activity Detection to skip silent parts...")

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=VAD_FILTER,
        vad_parameters={
            "threshold": VAD_THRESHOLD,
            "min_silence_duration_ms": VAD_MIN_SILENCE_DURATION_MS
        }
    )

    transcription = []
    segment_count = 0
    total_speech_duration = 0

    for segment in segments:
        transcription.append(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
        segment_count += 1
        total_speech_duration += (segment.end - segment.start)

    return "\n".join(transcription), info, segment_count, total_speech_duration

def main():
    # Start timer
    start_time = time.time()

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find all audio files
    print(f"Looking for audio files on {VOLUME_NAME}...")
    audio_files = find_all_audio_files()

    if not audio_files:
        print(f"No audio files found on the device.")
        return

    print(f"Found {len(audio_files)} audio file(s)")

    # Load the model once for all files
    print(f"Loading Whisper model (size: {MODEL_SIZE})...")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

    # Get today's date for the output filename
    today = datetime.now().strftime("%Y-%m-%d")
    date_filename = datetime.now().strftime("%m-%d-%Y")  # MM-DD-YYYY format

    # Prepare combined output
    all_transcriptions = []
    total_files_duration = 0
    total_files_speech = 0

    # Transcribe each file
    for idx, audio_file in enumerate(audio_files, 1):
        print(f"\n{'='*80}")
        print(f"Processing file {idx}/{len(audio_files)}")

        transcription, info, segment_count, total_speech_duration = transcribe_audio(audio_file, model)

        # Calculate time savings for this file
        total_duration = info.duration
        silence_duration = total_duration - total_speech_duration
        speech_percentage = (total_speech_duration / total_duration * 100) if total_duration > 0 else 0

        # Accumulate totals
        total_files_duration += total_duration
        total_files_speech += total_speech_duration

        # Format this file's output with AI-friendly structure
        all_transcriptions.append(f"\n## Recording {idx}: {os.path.basename(audio_file)}\n\n")
        all_transcriptions.append("**Recording Metadata:**\n")
        all_transcriptions.append(f"- Total Duration: {total_duration:.2f}s ({total_duration/60:.1f} minutes)\n")
        all_transcriptions.append(f"- Speech Duration: {total_speech_duration:.2f}s ({total_speech_duration/60:.1f} minutes)\n")
        all_transcriptions.append(f"- Silence Skipped: {silence_duration:.2f}s ({silence_duration/60:.1f} minutes)\n")
        all_transcriptions.append(f"- Speech Content: {speech_percentage:.1f}%\n")
        all_transcriptions.append(f"- Language: {info.language}\n")
        all_transcriptions.append(f"- Speech Segments: {segment_count}\n\n")
        all_transcriptions.append("**Transcript:**\n\n")
        all_transcriptions.append(transcription)
        all_transcriptions.append("\n\n")
        all_transcriptions.append("---\n")

    # Add summary header
    total_silence = total_files_duration - total_files_speech
    overall_speech_percentage = (total_files_speech / total_files_duration * 100) if total_files_duration > 0 else 0

    # Create AI-optimized header with context
    summary = []
    summary.append("# VOICE RECORDING TRANSCRIPTION\n\n")
    summary.append("## CONTEXT FOR AI ANALYSIS\n")
    summary.append("This document contains automatic transcriptions from voice recordings.\n")
    summary.append("The recordings were captured using a WS-852 dictaphone and transcribed using Whisper AI.\n")
    summary.append("Voice Activity Detection was used to skip silent portions.\n\n")

    summary.append("## INSTRUCTIONS FOR AI SUMMARIZATION\n")
    summary.append("When processing this document:\n")
    summary.append("- Extract key points, action items, and important information\n")
    summary.append("- Identify topics, themes, and categories\n")
    summary.append("- Maintain chronological order when relevant\n")
    summary.append("- Note any incomplete thoughts or unclear segments\n")
    summary.append("- If the user mentioned making bullet points, organize content accordingly\n")
    summary.append("- Preserve any lists, ideas, or structured thinking from the speaker\n\n")

    summary.append("## SESSION METADATA\n")
    summary.append(f"- **Transcription Date**: {today}\n")
    summary.append(f"- **Total Recordings**: {len(audio_files)} file(s)\n")
    summary.append(f"- **Total Audio Duration**: {total_files_duration/60:.1f} minutes ({total_files_duration/3600:.2f} hours)\n")
    summary.append(f"- **Actual Speech Content**: {total_files_speech/60:.1f} minutes ({overall_speech_percentage:.1f}% of total)\n")
    summary.append(f"- **Silence Skipped**: {total_silence/60:.1f} minutes\n\n")

    summary.append("---\n\n")
    summary.append("# TRANSCRIBED CONTENT\n\n")

    # Save transcription with date as markdown for better AI readability
    output_file = OUTPUT_DIR / f"{date_filename}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(summary)
        f.writelines(all_transcriptions)

    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"\n{'='*80}")
    print(f"All transcriptions saved to: {output_file}")
    print(f"Processed {len(audio_files)} file(s)")
    print(f"Total audio: {total_files_duration/60:.1f} min, speech: {total_files_speech/60:.1f} min ({overall_speech_percentage:.1f}%)")
    print(f"Skipped {total_silence/60:.1f} minutes of silence")
    print(f"Transcription success. Duration: {minutes} minutes and {seconds} seconds")

if __name__ == "__main__":
    main()
