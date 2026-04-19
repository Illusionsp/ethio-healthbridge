import os
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-1.5-flash"


def analyze_medicine_label(image_path: str) -> str:
    if not os.path.exists(image_path):
        return "ስህተት፡ የምስል ፋይል አልተገኘም።"

    print(f"Vision Engine analyzing: {image_path}")

    try:
        # Open image with Pillow and upload via new SDK
        img = Image.open(image_path)

        # Convert to bytes for upload
        import io
        buf = io.BytesIO()
        fmt = img.format or "JPEG"
        img.save(buf, format=fmt)
        buf.seek(0)

        mime = "image/jpeg" if fmt.upper() in ("JPEG", "JPG") else f"image/{fmt.lower()}"
        uploaded = _client.files.upload(
            file=buf,
            config=types.UploadFileConfig(mime_type=mime)
        )

        prompt = (
            "Analyze this medicine label image. Extract and translate to formal Amharic:\n"
            "1. የመድኃኒቱ ስም (Brand/Generic Name)\n"
            "2. የአጠቃቀም መመሪያ (How to use/Dosage)\n"
            "3. የሚያበቃበት ቀን (Expiry Date - Look for EXP/MFG)\n"
            "4. ጥንቃቄዎች (Warnings/Storage instructions)\n"
            "If the text is blurry or unreadable, say: 'ምስሉ ግልጽ ባለመሆኑ ማንበብ አልተቻለም።'"
        )

        response = _client.models.generate_content(
            model=MODEL,
            contents=[prompt, uploaded]
        )

        _client.files.delete(name=uploaded.name)
        return response.text.strip() if response.text else "ምስሉን ማንበብ አልተቻለም።"

    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "ይቅርታ፣ የቪዥን ሞተሩ ለጊዜው ተጨናንቋል። እባክዎ ከ1 ደቂቃ በኋላ ይሞክሩ።"
        print(f"Vision Error: {e}")
        return "ይቅርታ፣ ይሄንን ምስል መተንተን አልቻልኩም። እባክዎ ምስሉ ግልጽ መሆኑን ያረጋግጡ።"
