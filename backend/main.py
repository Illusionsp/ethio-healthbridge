import os
import shutil
import time
import re
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from cachetools import TTLCache

load_dotenv() 

from core.stt_engine import transcribe_amharic
from core.tts_engine import generate_voice_response
from core.rag_engine import query_medical_guidelines, generate_clinical_summary
from core.vision_eval import analyze_medicine_label
from utils.emergency import check_red_flags, get_emergency_message
from utils.mapping import extract_known_symptoms

try:
    from utils.telegram_bot import send_doctor_alert
except ImportError:
    def send_doctor_alert(*args, **kwargs): pass

OUTBREAK_THRESHOLD = 5

HOTSPOT_REGISTRY = {
    "Akaki-Kality": {"fever": 15, "chills": 12, "headache": 5},
    "Addis Ketema": {"cough": 8, "fever": 2},
    "Bole": {"fatigue": 2},
    "Kolfe Keranio": {"diarrhea": 4} 
}

def log_symptoms(sub_city: str, symptoms: list[str]) -> list[str]:
    outbreak_alerts = []
    if not sub_city or sub_city == "Unknown":
        return outbreak_alerts
        
    if sub_city not in HOTSPOT_REGISTRY:
        HOTSPOT_REGISTRY[sub_city] = {}
        
    for sym in symptoms:
        current_count = HOTSPOT_REGISTRY[sub_city].get(sym, 0)
        HOTSPOT_REGISTRY[sub_city][sym] = current_count + 1
        
        if HOTSPOT_REGISTRY[sub_city][sym] == OUTBREAK_THRESHOLD:
            alert = f"⚠️ ማስጠንቀቂያ፡ ከፍተኛ የ'{sym}' ስርጭት በ{sub_city} ተገኝቷል።"
            print(alert)
            outbreak_alerts.append(alert)
            
    return outbreak_alerts

def clean_latin_script(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'\s*\([^)]*[a-zA-Z][^)]*\)', '', text)
    cleaned = re.sub(r'[a-zA-Z]+', '', cleaned)
    return cleaned.strip()

app = FastAPI(title="Tena LeAdam (ጤናለአዳም) API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/audio_outputs", exist_ok=True)
os.makedirs("data/temp", exist_ok=True)
os.makedirs("data/guidelines", exist_ok=True)

app.mount("/pdfs", StaticFiles(directory="data/guidelines"), name="pdfs")

async def delete_old_files():
    while True:
        await asyncio.sleep(300)
        now = time.time()
        for directory in ["data/audio_outputs", "data/temp"]:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath):
                        if now - os.path.getmtime(filepath) > 300:
                            try:
                                os.remove(filepath)
                            except Exception:
                                pass

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(delete_old_files())

class TextQuery(BaseModel):
    text: str
    sub_city: str = "Unknown"
    user_id: str = "guest_user"

response_cache = TTLCache(maxsize=100, ttl=3600)

@app.post("/api/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...), 
    sub_city: str = Form("Unknown"),
    user_id: str = Form("guest_user")
):
    temp_audio_path = f"data/temp/{audio.filename}"
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        transcribed_text = transcribe_amharic(temp_audio_path)
        extracted_symptoms = extract_known_symptoms(transcribed_text)
        
        log_symptoms(sub_city, extracted_symptoms)
        
        if check_red_flags(transcribed_text):
            # FIXED: Create an instant emergency summary instead of 'None'
            emergency_summary = {
                "symptoms": extracted_symptoms if extracted_symptoms else ["Critical Emergency"],
                "urgency": "🔴 RED FLAG (High Priority)",
                "ai_analysis": "System detected life-threatening keywords bypassing standard AI triage.",
                "recommended_action": "Immediate medical callback/dispatch required."
            }
            
            rag_result = {
                "response_text": get_emergency_message(), 
                "citations": [], 
                "patient_summary": emergency_summary
            }
            emergency_status = True
        else:
            emergency_status = False
            enhanced_query = f"{transcribed_text} ({', '.join(extracted_symptoms)})" if extracted_symptoms else transcribed_text
            
            rag_result = query_medical_guidelines(enhanced_query, user_id=user_id)

        patient_summary = rag_result.get("patient_summary")
        alert_sent = False
        if patient_summary:
            patient_summary["patient_id"] = user_id
            patient_summary["raw_amharic"] = transcribed_text
            if emergency_status:
                send_doctor_alert(patient_summary)
                alert_sent = True
                
        if isinstance(rag_result, dict):
            rag_response_text = rag_result.get("response_text", "")
            citations = rag_result.get("citations", [])
        else:
            rag_response_text = str(rag_result)
            citations = []
            
        safe_amharic_text = clean_latin_script(rag_response_text)
        response_audio_path = await generate_voice_response(safe_amharic_text)
        
        return {
            "transcription": transcribed_text,
            "response_text": safe_amharic_text,
            "audio_url": f"/api/audio/{os.path.basename(response_audio_path)}" if response_audio_path else None,
            "emergency": emergency_status,
            "alert_sent": alert_sent,
            "citations": citations,
            "patient_summary": patient_summary
        }
    except Exception as e:
        print("\n❌--- የሲስተም ስህተት ሪፖርት ---❌")
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
        extracted_symptoms = extract_known_symptoms(query.text)
        
        log_symptoms(query.sub_city, extracted_symptoms)
        
        # Changed 'transcribed_text' to 'query.text'
        if check_red_flags(query.text):
            emergency_summary = {
                "symptoms": extracted_symptoms if extracted_symptoms else ["Critical Emergency"],
                "urgency": "🔴 RED FLAG (High Priority)",
                "ai_analysis": "System detected life-threatening keywords bypassing standard AI triage.",
                "recommended_action": "Immediate medical callback/dispatch required."
            }
            
            rag_result = {
                "response_text": get_emergency_message(), 
                "citations": [], 
                "patient_summary": emergency_summary
            }
            emergency_status = True
        else:
            emergency_status = False
            
            rag_result = query_medical_guidelines(query.text, user_id=query.user_id)

        patient_summary = rag_result.get("patient_summary")
        alert_sent = False
        if patient_summary:
            patient_summary["patient_id"] = query.user_id
            patient_summary["raw_amharic"] = query.text
            if emergency_status:
                send_doctor_alert(patient_summary)
                alert_sent = True
                
        if isinstance(rag_result, dict):
            rag_response_text = rag_result.get("response_text", "")
            citations = rag_result.get("citations", [])
        else:
            rag_response_text = str(rag_result)
            citations = []
            
        safe_amharic_text = clean_latin_script(rag_response_text)
        response_audio_path = await generate_voice_response(safe_amharic_text)
        
        return {
            "response_text": safe_amharic_text,
            "audio_url": f"/api/audio/{os.path.basename(response_audio_path)}" if response_audio_path else None,
            "emergency": emergency_status,
            "alert_sent": alert_sent,
            "citations": citations,
            "patient_summary": patient_summary
        }
    except Exception as e:
        print("\n❌--- የሲስተም ስህተት ሪፖርት ---❌")
        import traceback
        traceback.print_exc()
        print("❌----------------------------❌\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vision-analyze")
async def vision_analyze(image: UploadFile = File(...)):
    temp_img_path = f"data/temp/{image.filename}"
    with open(temp_img_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
        
    try:
        analysis_text = analyze_medicine_label(temp_img_path)
        
        safe_amharic_text = clean_latin_script(analysis_text)
        response_audio_path = await generate_voice_response(safe_amharic_text)
        
        return {
            "analysis": safe_amharic_text,
            "audio_url": f"/api/audio/{os.path.basename(response_audio_path)}" if response_audio_path else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            
@app.post("/api/hakim-yamakru")
async def consult_doctor(summary: dict):
    try:
        success = send_doctor_alert(summary)
        if success:
            return {"status": "success", "message": "Alert sent to doctor."}
        else:
            raise HTTPException(status_code=500, detail="Failed to send Telegram alert.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hotspots")
async def get_hotspots():
    return {"status": "success", "data": HOTSPOT_REGISTRY}

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    file_path = f"data/audio_outputs/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Audio not found")