from fastapi import APIRouter, Form
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

router = APIRouter(prefix="/api/rag")

@router.post("/ask")
async def rag_ask(query: str = Form(...)):
    """EPHCG guideline answers from transcribed text"""
    prompt = f"""
    You are Ethio-HealthBridge AI doctor using EPHCG guidelines.
    Answer in Amharic only. Be clear for rural patients.
    
    Question: {query}
    
    EPHCG Answer:"""
    
    response = model.generate_content(prompt)
    return {"answer": response.text, "query": query}