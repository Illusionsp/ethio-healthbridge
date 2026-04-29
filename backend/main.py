from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import stt, tts, chat, vision, safety
from app.api import assistant as assistant_router

app = FastAPI(title="Ethio‑HealthBridge Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stt.router, prefix="/stt", tags=["Speech-to-Text"])
app.include_router(tts.router, prefix="/tts", tags=["Text-to-Speech"])
app.include_router(chat.router, prefix="/chat", tags=["RAG Chat"])
app.include_router(vision.router, prefix="/vision", tags=["Vision"])
app.include_router(safety.router, prefix="/safety", tags=["Safety"])


app.include_router(assistant_router.router)