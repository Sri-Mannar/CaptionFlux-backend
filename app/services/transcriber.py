# app/services/transcriber.py
import whisper
import os, logging

# Load model once (at startup)
# You can change 'small' -> 'base' or 'medium' later for accuracy vs speed.
model = whisper.load_model("small")

def transcribe_audio(audio_path: str):
    """Transcribes an audio file using Whisper and returns text + timestamps."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logging.info(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path, verbose=False)

    # Each segment has start, end, and text
    segments = [
        {"start": round(seg["start"], 2), "end": round(seg["end"], 2), "text": seg["text"].strip()}
        for seg in result.get("segments", [])
    ]

    # Combine text for readability
    full_text = " ".join(seg["text"] for seg in segments)

    return {
        "success": True,
        "text": full_text,
        "segments": segments,
        "language": result.get("language", "unknown"),
    }
