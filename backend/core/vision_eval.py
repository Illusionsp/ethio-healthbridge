import google.generativeai as genai
import os
from PIL import Image
from utils.text_utils import clean_latin_script

def analyze_medicine_label(image_path: str) -> str:
    if not os.path.exists(image_path):
        return "ስህተት፡ የምስል ፋይል አልተገኘም።"
        
    print(f"👁️ የቪዥን ሞተር ምስሉን እየተነተነ ነው፡ {image_path}")
    
    try:
        # Using the specific hackathon-optimized model
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        img = Image.open(image_path)
        
        # EXTREMELY AGGRESSIVE prompt to enforce Zero-English
        prompt = (
            "በምስሉ ላይ የሚታየውን የመድኃኒት መረጃ በጥልቀት ይተንትኑ። የሚከተሉትን ነጥቦች በባለሙያ ዶክተር ቃና እና በንጹህ አማርኛ ፊደል ብቻ ያቅርቡ።\n\n"
            "ክሪቲካል ሕግ (CRITICAL RULE):\n"
            "1. ምንም አይነት የእንግሊዝኛ ፊደል (A-Z) አይጻፉ። በፍጹም!\n"
            "2. በቅንፍ ውስጥ የእንግሊዝኛ ትርጉም ማስቀመጥ (ወይም ሌላ ማንኛውም የእንግሊዝኛ ቃል) ተለይቶ የተከለከለ ነው።\n"
            "3. ሁሉንም የሕክምና ቃላት፣ የመድኃኒት ስሞች፣ እና መለኪያዎች (እንደ ml, mg) ወደ አማርኛ ፊደል ብቻ ይለውጡ።\n\n"
            "ሊተነተኑ የሚገባቸው ነጥቦች፡\n"
            "1. የመድኃኒቱ ሙሉ ስም እና ይዘት (ለምሳሌ፡ አሞክሲሲሊን)\n"
            "2. መመሪያው (እንዴት መወሰድ እንዳለበት)\n"
            "3. የሚያበቃበት ቀን\n"
            "4. አምራች ድርጅት\n"
            "5. ዋና ዋና ማስጠንቀቂያዎች እና የጎንዮሽ ጉዳቶች\n\n"
            "ጠቃሚ፦ ንጹህ አማርኛ ብቻ ይጠቀሙ። ምስሉ ግልጽ ካልሆነ፡ 'ይቅርታ ምስሉ ግልጽ ባለመሆኑ ማንበብ አልተቻለም።' ይበሉ።"
        )
        
        response = model.generate_content([prompt, img])
        unfiltered_text = response.text.strip()
        
        # PROGRAMMATIC HARD-ENFORCEMENT (Safety Layer)
        return clean_latin_script(unfiltered_text)
    except Exception as e:
        if "429" in str(e):
            return "ይቅርታ፣ የቪዥን ሞተሩ ለጊዜው ተጨናንቋል። እባክዎ ከ1 ደቂቃ በኋላ ይሞክሩ።"
        print(f"የቪዥን ስህተት፡ {e}")
        return "ይቅርታ፣ ይሄንን ምስል መተንተን አልቻልኩም። እባክዎ ምስሉ ግልጽ መሆኑን ያረጋግጡ።"