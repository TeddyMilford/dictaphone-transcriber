#!/usr/bin/env python3
"""
Summarize a transcription using Claude API and email the summary via Mailgun.

Usage:
    python3 summarize_and_email.py <transcript_path>
    python3 summarize_and_email.py  # defaults to today's transcript
"""
import os
import sys
from pathlib import Path
from datetime import datetime

import anthropic
import requests
from dotenv import load_dotenv

# Load .env from the script's directory
load_dotenv(Path(__file__).parent / ".env")

# Configuration from environment
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", "")
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "")

TRANSCRIPTIONS_DIR = Path.home() / "Desktop" / "Transcriptions"
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

SUMMARY_PROMPT = """\
You are summarizing a day's worth of voice recordings from a dictaphone. The transcript \
contains a mix of work tasks, personal reminders, ideas, and random thoughts captured \
throughout the day.

Produce a clear, well-organized summary with these sections:

## Action Items
Concrete tasks that need to be done, with any deadlines or people mentioned.

## Work Notes
Key points from meetings, projects, decisions, and work-related observations.

## Personal / Errands
Personal reminders, errands, appointments, and non-work items.

## Ideas & Thoughts
Interesting ideas, things to explore, recommendations, and general musings.

Rules:
- Be concise but don't drop important details (names, dates, numbers, specifics).
- Use bullet points within each section.
- If a topic spans multiple recordings, consolidate it into one bullet.
- Skip the AI instructions header from the transcript -- just summarize the actual content.
- Do not include timestamps.
"""


def get_transcript_path(args):
    """Determine which transcript file to process."""
    if args:
        path = Path(args[0])
        if path.exists():
            return path
        print(f"Error: File not found: {path}")
        sys.exit(1)

    # Default to today's transcript
    today = datetime.now().strftime("%m-%d-%Y")
    path = TRANSCRIPTIONS_DIR / f"{today}.md"
    if path.exists():
        return path

    print(f"Error: No transcript found for today ({today}.md)")
    print(f"Looked in: {TRANSCRIPTIONS_DIR}")
    sys.exit(1)


def validate_config():
    """Check that all required env vars are set."""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not MAILGUN_API_KEY:
        missing.append("MAILGUN_API_KEY")
    if not MAILGUN_DOMAIN:
        missing.append("MAILGUN_DOMAIN")
    if not EMAIL_FROM:
        missing.append("EMAIL_FROM")
    if not EMAIL_TO:
        missing.append("EMAIL_TO")

    if missing:
        print("Error: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nCopy .env.example to .env and fill in your values:")
        print("  cp .env.example .env")
        sys.exit(1)


def summarize_transcript(transcript_text):
    """Send transcript to Claude and return the summary."""
    print(f"Sending transcript to Claude ({CLAUDE_MODEL})...")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"{SUMMARY_PROMPT}\n\n---\n\nHere is the transcript:\n\n{transcript_text}",
            }
        ],
    )

    summary = message.content[0].text
    print(f"Summary generated ({message.usage.input_tokens} input, {message.usage.output_tokens} output tokens)")
    return summary


def send_email(subject, body):
    """Send the summary email via Mailgun."""
    print(f"Sending email via Mailgun to {EMAIL_TO}...")

    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": EMAIL_FROM,
            "to": [EMAIL_TO],
            "subject": subject,
            "text": body,
        },
    )

    if response.status_code == 200:
        print("Email sent successfully.")
    else:
        print(f"Email failed (HTTP {response.status_code}): {response.text}")
        sys.exit(1)


def main():
    validate_config()

    transcript_path = get_transcript_path(sys.argv[1:])
    print(f"Processing: {transcript_path.name}")

    transcript_text = transcript_path.read_text(encoding="utf-8")

    summary = summarize_transcript(transcript_text)

    # Save summary locally alongside the transcript
    summary_path = transcript_path.with_name(transcript_path.stem + "_summary.md")
    summary_path.write_text(summary, encoding="utf-8")
    print(f"Summary saved to: {summary_path}")

    # Email the summary
    date_str = datetime.now().strftime("%B %d, %Y")
    subject = f"Dictaphone Summary - {date_str}"
    send_email(subject, summary)

    print("Done.")


if __name__ == "__main__":
    main()
