# app/routes/transcribe.py
from fastapi import APIRouter, HTTPException, Query
from app.services.transcriber import transcribe_audio
import logging

router = APIRouter(prefix="/transcribe", tags=["Transcribe"])

@router.get("/")
async def transcribe(audio_path: str = Query(..., description="Path to .wav file")):
    """
    Transcribes the provided audio file (from uploads or fetched).
    Returns text and caption segments with timestamps.
    """
    try:
        result = transcribe_audio(audio_path)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audio file not found.")
    except Exception as e:
        logging.exception("Transcription failed")
        raise HTTPException(status_code=500, detail=str(e))
