# app/services/audio_utils.py
import subprocess, os

def extract_audio(input_path: str) -> str:
    """Extracts mono 16 kHz WAV from audio/video file using ffmpeg (Windows-safe)."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = input_path + ".wav"
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", output_path
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        err = proc.stderr.decode(errors="ignore")
        raise RuntimeError(f"FFmpeg failed: {err}")

    if not os.path.exists(output_path):
        raise RuntimeError(f"Output file missing: {output_path}")

    return output_path
