import google.generativeai as genai
import os
from PIL import Image

def analyze_medicine_label(image_path: str) -> str:
    if not os.path.exists(image_path):
        return "ስህተት፡ የምስል ፋይል አልተገኘም።"
        
    print(f"👁️ Vision Engine analyzing: {image_path}")
    
    try:
        # SWITCHED to 2.5-flash-lite for better speed and quota
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        img = Image.open(image_path)
        
        # Refined prompt for more professional medical Amharic
        prompt = (
            "Analyze this medicine label image. Extract and translate to formal Amharic:\n"
            "1. የመድኃኒቱ ስም (Brand/Generic Name)\n"
            "2. የአጠቃቀም መመሪያ (How to use/Dosage)\n"
            "3. የሚያበቃበት ቀን (Expiry Date - Look for EXP/MFG)\n"
            "4. ጥንቃቄዎች (Warnings/Storage instructions)\n"
            "If the text is blurry or unreadable, say: 'ምስሉ ግልጽ ባለመሆኑ ማንበብ አልተቻለም።'"
        )
        
        response = model.generate_content([prompt, img])
        return response.text.strip()
    except Exception as e:
        if "429" in str(e):
            return "ይቅርታ፣ የቪዥን ሞተሩ ለጊዜው ተጨናንቋል። እባክዎ ከ1 ደቂቃ በኋላ ይሞክሩ።"
        print(f"Vision Error: {e}")
        return "ይቅርታ፣ ይሄንን ምስል መተንተን አልቻልኩም። እባክዎ ምስሉ ግልጽ መሆኑን ያረጋግጡ።"