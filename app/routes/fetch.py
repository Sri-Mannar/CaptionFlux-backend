# app/routes/fetch.py
from fastapi import APIRouter, HTTPException, Query
import os, uuid, subprocess, logging

router = APIRouter(prefix="/fetch", tags=["Fetch"])

FETCH_DIR = "fetched"
os.makedirs(FETCH_DIR, exist_ok=True)

@router.get("/")
async def fetch_audio(url: str = Query(..., description="YouTube or media URL")):
    """
    Downloads audio from a YouTube (or any online) source and extracts mono 16kHz WAV.
    """
    try:
        file_id = uuid.uuid4().hex
        temp_audio = os.path.join(FETCH_DIR, f"{file_id}_temp.m4a")
        output_wav = temp_audio + ".wav"

        # Step 1: Download best available audio with yt-dlp
        download_cmd = [
            "yt-dlp",
            "-f", "bestaudio",
            "-o", temp_audio,
            url,
        ]
        logging.info(f"Downloading audio from {url}")
        subprocess.run(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Step 2: Convert to mono 16kHz WAV
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", temp_audio,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            output_wav
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Step 3: Cleanup temporary file
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

        logging.info(f"Fetched audio: {output_wav}")
        return {"success": True, "audio_path": output_wav}

    except subprocess.CalledProcessError as e:
        logging.exception("Download or conversion failed")
        raise HTTPException(status_code=500, detail=f"Audio fetch failed: {e.stderr.decode(errors='ignore') if e.stderr else str(e)}")

    except Exception as e:
        logging.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))
