# app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import os, uuid, logging
from app.services.audio_utils import extract_audio

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Optional: setup simple logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = uuid.uuid4().hex
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(input_path, "wb") as f:
            f.write(await file.read())

        audio_path = extract_audio(input_path)
        logging.info(f"Extracted audio: {audio_path}")

        return {"success": True, "audio_path": audio_path}

    except Exception as e:
        logging.exception("Upload or extraction failed")
        raise HTTPException(status_code=500, detail="Audio extraction failed. Please try again.")
