from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from app.services.tts_service import synthesize_amharic

router = APIRouter(prefix="/tts", tags=["tts"])

class TTSRequest(BaseModel):
    text: str

@router.post("/amharic")
async def tts_amharic(body: TTSRequest):
    filename = synthesize_amharic(body.text)
    filepath = Path("audio") / filename
    return FileResponse(
        path=str(filepath),
        media_type="audio/mpeg",
        filename=filename,
    )