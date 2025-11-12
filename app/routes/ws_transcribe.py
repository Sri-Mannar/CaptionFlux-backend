# app/routes/ws_transcribe.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio, os, tempfile, logging, subprocess
import whisper
from pydub import AudioSegment

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Load model once
model = whisper.load_model("small")

@router.websocket("/transcribe")
async def websocket_transcribe(ws: WebSocket):
    await ws.accept()
    logging.info("WebSocket connected for streaming transcription")

    try:
        # Expect JSON: {"audio_path": "uploads/abcd.wav"}
        init_msg = await ws.receive_json()
        audio_path = init_msg.get("audio_path")
        # Safely resolve path relative to backend root
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(base_dir, "../../"))  # move 2 levels up
        resolved_path = os.path.join(root_dir, audio_path)
        resolved_path = os.path.normpath(resolved_path)  # normalize slashes for Windows

        if not audio_path or not os.path.exists(resolved_path):
            await ws.send_json({"error": f"File not found: {resolved_path}"})
            await ws.close()
            return

        # Process in chunks
        CHUNK_DURATION = 10 * 1000  # 10 seconds (pydub uses ms)
        audio = AudioSegment.from_file(resolved_path)
        total_duration = len(audio)

        for start in range(0, total_duration, CHUNK_DURATION):
            end = min(start + CHUNK_DURATION, total_duration)
            chunk = audio[start:end]

            # Save temp chunk
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                chunk.export(tmp.name, format="wav")
                chunk_path = tmp.name

            # Transcribe this chunk  language="en"
            result = model.transcribe(
                chunk_path,
                no_speech_threshold=0.1,
                logprob_threshold=-2.0,
                condition_on_previous_text=False,
            )

            os.remove(chunk_path)

            for seg in result.get("segments", []):
                seg_data = {
                    "start": round(seg["start"] + start / 1000, 2),
                    "end": round(seg["end"] + start / 1000, 2),
                    "text": seg["text"].strip(),
                }
                await ws.send_json(seg_data)

            # Small sleep to simulate “real-time”
            await asyncio.sleep(0.1)

        await ws.send_json({"done": True})
        await ws.close()
        logging.info("WebSocket closed normally")

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected by client")

    except Exception as e:
        logging.exception("Error in streaming transcription")
        await ws.send_json({"error": str(e)})
        await ws.close()
