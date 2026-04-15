import google.generativeai as genai
import os
from PIL import Image

if "GOOGLE_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def analyze_medicine_label(image_path: str) -> str:
    """Analyzes a medicine label image using Gemini Vision."""
    if not os.path.exists(image_path):
        return "ስህተት፡ የምስል ፋይል አልተገኘም። (Error: Image not found.)"
        
    print(f"👁️ Vision Engine analyzing: {image_path}")
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        img = Image.open(image_path)
        
        prompt = (
            "Analyze this medicine label. "
            "Please extract the following information and output it in Amharic:\n"
            "1. መድሃኒቱ ስም (Medicine Name)\n"
            "2. አጠቃቀም (Usage/Dosage)\n"
            "3. የሚያበቃበት ጊዜ (Expiry Date)\n"
            "4. ማስጠንቀቂያ (Warnings, if any)\n"
            "If you cannot find an expiry date, explicitly state that."
        )
        
        response = model.generate_content([prompt, img])
        return response.text.strip()
    except Exception as e:
        print(f"Vision Eval Error: {e}")
        return "ይቅርታ፣ ይሄንን ምስል መተንተን አልቻልኩም። እባክዎ ምስሉ ግልጽ መሆኑን ያረጋግጡ። (Sorry, I couldn't analyze the image.)"

if __name__ == "__main__":
    
    pass
