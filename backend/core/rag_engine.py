import os
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.llms import MockLLM
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from google import genai as google_genai
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GEMINI_API_KEY")
_genai_client = google_genai.Client(api_key=_api_key)
LLM_MODEL = "gemini-2.5-flash-lite"

try:
    # Use MockLLM for retrieval only — we call Gemini directly for generation
    Settings.llm = MockLLM()
    Settings.embed_model = GoogleGenAIEmbedding(
        model_name="models/gemini-embedding-001",
        api_key=_api_key
    )
except Exception as e:
    print(f"Warning: Could not initialize embedding model. {e}")

DB_PATH = "data/vector_db"

GREETINGS = [
    "hi", "hello", "hey",
    "ሰላም", "ጤና ይስጥልኝ",
    "akkam", "nagaa", "salaam",
    "ሰላም ኩን", "ከመይ ኣለኻ",
]


def detect_language(text: str) -> str:
    amharic_chars = set("አበቀደዘሀለሐሠረሰሸቀቐቤነኘአከኸወዐዘዠየደጀጠጨጰጸፀፈፐ")
    text_lower = text.lower()
    amharic_count = sum(1 for c in text if c in amharic_chars)
    latin_count = sum(1 for c in text_lower if c.isalpha() and c.isascii())
    if amharic_count > latin_count:
        tigrinya_markers = ["ቃንዛ", "ምስትንፋስ", "ድኻምነት", "ምዝዛም", "ሳዕሪ", "ረስኒ"]
        if any(m in text for m in tigrinya_markers):
            return "Tigrinya"
        return "Amharic"
    oromoo_markers = ["dhukkuba", "qufaa", "garaa", "lafee", "hargansa", "qurxummii"]
    if any(m in text_lower for m in oromoo_markers):
        return "Afaan Oromoo"
    return "Amharic"


def get_db_collection():
    os.makedirs(DB_PATH, exist_ok=True)
    db = chromadb.PersistentClient(path=DB_PATH)
    return db.get_or_create_collection("moh_guidelines")


def _llm_complete(prompt: str) -> str:
    """Call Gemini directly via google-genai SDK."""
    response = _genai_client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )
    return response.text.strip() if response.text else ""


def query_medical_guidelines(query_text: str, mode: str = "adult") -> str:
    print(f"RAG query: '{query_text}' | mode: {mode}")

    if not query_text or not query_text.strip():
        return "እባክዎ ጥያቄዎን በድጋሚ ይናገሩ። ድምፅዎ አልተሰማም።"

    if query_text.lower().strip() in GREETINGS:
        return (
            "ጤና ይስጥልኝ! እኔ Ethio-HealthBridge ነኝ። "
            "በኢትዮጵያ ጤና ሚኒስቴር መመሪያዎች ላይ ተመስርቼ ስለ ጤናዎ መረጃ ልሰጥዎ እችላለሁ። "
            "እንዴት ልርዳዎ? / Akkam gargaaruu danda'a? / ብኸመይ ክሕግዘካ እኽእል?"
        )

    detected_lang = detect_language(query_text)
    print(f"Detected language: {detected_lang}")

    try:
        collection = get_db_collection()

        if collection.count() == 0:
            return _basic_llm_response(detected_lang)

        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store, storage_context=storage_context
        )

        query_engine = index.as_query_engine(similarity_top_k=3)
        response = query_engine.query(query_text)

        source_texts = "\n\n".join([
            f"Source (Score: {node.score:.2f}):\n{node.text}"
            for node in response.source_nodes
        ])

        sources = list({
            f"{node.metadata.get('file_name','MoH Document')} (ገጽ {node.metadata.get('page_label','N/A')})"
            for node in response.source_nodes
        })
        source_string = ", ".join(sources)

        if detected_lang == "Afaan Oromoo":
            lang_instruction = "Respond in clear, simple Afaan Oromoo. Start with: 'Akkaadamii MoH irratti hundaa\\'uudhaan:'"
        elif detected_lang == "Tigrinya":
            lang_instruction = "Respond in clear, simple Tigrinya. Start with: 'ብመሰረት መምርሒ ሚኒስትሪ ጥዕና ኢትዮጵያ:'"
        else:
            lang_instruction = f"Respond in formal Amharic. Start with: 'በኢትዮጵያ ጤና ሚኒስቴር መመሪያ መሰረት ({source_string})፦'"

        child_instruction = ""
        if mode == "child":
            child_instruction = (
                "\nCHILD HEALTH MODE: Patient is a child. Ask for age/weight if not given. "
                "Adjust dosage for pediatric use. Flag symptoms needing immediate hospital visit."
            )

        prompt = f"""You are 'Ethio-HealthBridge', a professional Medical AI for Ethiopia.
Give a culturally respectful health guidance response based ONLY on the retrieved context below.

LANGUAGE: {lang_instruction}{child_instruction}

RULES:
1. Only use information from the context. No hallucination.
2. If symptoms are vague, ask for more details.
3. If context doesn't answer, say so and advise visiting a clinic.
4. Keep response concise and easy to understand.

SYMPTOM HINTS: "mitch"/"ምች"=fever/viral, "wugat"/"ውጋት"=sharp pain, "qurxummii"=malaria-like fever, "hargansa"=breathing difficulty

USER QUERY: {query_text}

RETRIEVED MoH CONTEXT:
{source_texts}

Provide the final response:"""

        return _llm_complete(prompt)

    except Exception as e:
        print(f"RAG Error: {e}")
        return "ይቅርታ፣ አሁን ላይ መረጃ ማግኘት አልቻልኩም። እባክዎ ወደ ጤና ተቋም ይሂዱ።"


def _basic_llm_response(lang: str = "Amharic") -> str:
    if lang == "Afaan Oromoo":
        return "Galmeen fayyaa amma duwwaa dha. Hatattama: 912"
    if lang == "Tigrinya":
        return "ዳታቤዝ ሕክምና ሕጂ ባዶ እዩ። ህጹጽ: 912"
    return "የሕክምና መመሪያ ማከማቻው ባዶ ነው። ድንገተኛ: 912"
