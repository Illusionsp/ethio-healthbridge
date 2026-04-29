# app/api/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services import rag_service

router = APIRouter()

# Optional: broader headache patterns
HEADACHE_PATTERNS = [
    "ራስ ምታት",
    "ራሴን ያመኛል",
    "ራሴ ይህላል",
    "ራሴ ይዞኛል",
]

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    query: str
    answer_am: str
    sources: list[dict]


@router.post("/amharic", response_model=ChatResponse)
async def chat_amharic(req: ChatRequest):
    query = req.query.strip()

    # 1) Retrieve REAL context from ChromaDB (not dummy)
    context_docs = rag_service.retrieve_context(query, top_k=3)

    # 2) Build prompt (for future LLM use, not used in logic yet)
    prompt = rag_service.build_prompt_amharic(query, context_docs)

    # 3) For now, simulate an answer using simple rules
    if "የደም ግፊት" in query:
        answer = (
            "የደም ግፊት ከፍተኛ ከሆነ በየቀኑ መለካት፣ "
            "ጨው መቀነስ፣ ከባድ ስኪን መቆጣጠር እና ስራ ተንቀሳቃሽነት መጨመር ይመከራል። "
            "ከባድ ምልክቶች ካሉ ወዲያውኑ ወደ ቅርብ የጤና ጣቢያ ያመለከቱ።"
        )
    # OLD: elif "ራስ ምታት" in query:
    # NEW: match any common headache phrasing
    elif any(p in query for p in HEADACHE_PATTERNS):
        answer = (
            "ቀላል ወይም መካከለኛ ራስ ምታት ብዙ ጊዜ በድካም ወይም በውሃ እጥረት ሊመጣ ይችላል። "
            "እረፍት መውሰድ፣ ብዙ ውሃ መጠጣት እና ብዙ ቡና እና ከባድ ስኪን መቆጣጠር ይመከራል። "
            "ራስ ምታቱ በጣም ከባድ ከሆነ፣ ዓይን መቀየር ወይም እጅና እግር ድንገተኛ መውደቅ ካለ "
            "ወዲያውኑ ወደ ሐኪም ይመለከቱ።"
        )
    else:
        answer = (
            "የጤና ሁኔታዎን በተመራማሪ መመሪያ መሰረት ለመገምገም ተጨማሪ መረጃ ያስፈልጋል። "
            "እባክዎ የምታስቸግሮትን ምልክቶች በዝርዝር ይገልጹ። "
            "ከባድ ህመም ወይም ድንገተኛ ሁኔታ ካለ ወዲያውኑ ወደ 911/912 ይደውሉ።"
        )

    return ChatResponse(
        query=query,
        answer_am=answer,
        sources=context_docs,
    )