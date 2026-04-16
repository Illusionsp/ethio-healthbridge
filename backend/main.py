from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil
from dotenv import load_dotenv
from cachetools import TTLCache

load_dotenv() 

from core.stt_engine import transcribe_amharic
from core.tts_engine import generate_voice_response
from core.rag_engine import query_medical_guidelines
from core.vision_eval import analyze_medicine_label
from utils.emergency import check_red_flags, get_emergency_message
from utils.mapping import extract_known_symptoms

app = FastAPI(title="Ethio-HealthBridge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIXED: Removed 'backend/' so it uses the correct current folder
os.makedirs("data/audio_outputs", exist_ok=True)
os.makedirs("data/temp", exist_ok=True)

class TextQuery(BaseModel):
    text: str

response_cache = TTLCache(maxsize=100, ttl=3600)

@app.post("/api/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):
    # FIXED: Removed 'backend/'
    temp_audio_path = f"data/temp/{audio.filename}"
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        transcribed_text = transcribe_amharic(temp_audio_path)
        
        if check_red_flags(transcribed_text):
            rag_response = get_emergency_message()
            emergency_status = True
        else:
            emergency_status = False
            extracted_symptoms = extract_known_symptoms(transcribed_text)
            
            if extracted_symptoms:
                enhanced_query = f"{transcribed_text} ({', '.join(extracted_symptoms)})"
            else:
                enhanced_query = transcribed_text
                
            if enhanced_query in response_cache:
                rag_response = response_cache[enhanced_query]
            else:
                rag_response = query_medical_guidelines(enhanced_query)
                response_cache[enhanced_query] = rag_response
                
        response_audio_path = generate_voice_response(rag_response)
        
        return {
            "transcription": transcribed_text,
            "response_text": rag_response,
            "audio_url": f"/api/audio/{os.path.basename(response_audio_path)}",
            "emergency": emergency_status
        }
    except Exception as e:
        print("\n❌--- FASTAPI CRASH REPORT ---❌")
        import traceback
        traceback.print_exc()
        print("❌----------------------------❌\n")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

@app.post("/api/text-chat")
async def text_chat(query: TextQuery):
    try:
        if check_red_flags(query.text):
            rag_response = get_emergency_message()
            emergency_status = True
        else:
            emergency_status = False
            extracted_symptoms = extract_known_symptoms(query.text)
            
            if extracted_symptoms:
                enhanced_query = f"{query.text} ({', '.join(extracted_symptoms)})"
            else:
                enhanced_query = query.text
                
            if enhanced_query in response_cache:
                rag_response = response_cache[enhanced_query]
            else:
                rag_response = query_medical_guidelines(enhanced_query)
                response_cache[enhanced_query] = rag_response
                
        response_audio_path = generate_voice_response(rag_response)
        
        return {
            "response_text": rag_response,
            "audio_url": f"/api/audio/{os.path.basename(response_audio_path)}" if response_audio_path else None,
            "emergency": emergency_status
        }
    except Exception as e:
        print("\n❌--- FASTAPI CRASH REPORT ---❌")
        import traceback
        traceback.print_exc()
        print("❌----------------------------❌\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vision-analyze")
async def vision_analyze(image: UploadFile = File(...)):
    # FIXED: Removed 'backend/'
    temp_img_path = f"data/temp/{image.filename}"
    with open(temp_img_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
        
    try:
        analysis_result = analyze_medicine_label(temp_img_path)
        return {"analysis": analysis_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)

# THIS IS THE PART THAT WAS CAUSING THE 404!
@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    # FIXED: Removed 'backend/'
    file_path = f"data/audio_outputs/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Audio not found")