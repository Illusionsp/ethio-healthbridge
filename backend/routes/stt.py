from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

# IMPORTANT: use ElevenLabs as the active STT backend
from app.services import stt_service_elevenlabs as stt_service

router = APIRouter()

@router.post("/amharic", response_class=JSONResponse)
async def speech_to_text_amharic(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    try:
        result = stt_service.transcribe_amharic(audio_bytes)
        return result
    except Exception as e:
        return JSONResponse({"error": f"STT failed: {str(e)}"}, status_code=500)