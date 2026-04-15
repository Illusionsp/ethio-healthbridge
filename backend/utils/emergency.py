RED_FLAGS_AMHARIC = [
    "ደረት ህመም",
    "የመተንፈስ ችግር",
    "መሳት",
    "ብዙ ደም",
    "የመናገር ችግር",
    "ድንገተኛ ድክመት",
    "መመረዝ",
    "መቃጠል"
]

def check_red_flags(transcribed_text: str) -> bool:
    text_lower = transcribed_text.replace("፣", " ").replace("።", " ")
    
    for flag in RED_FLAGS_AMHARIC:
        if flag in text_lower:
            print(f"🚨 EMERGENCY DETECTED: {flag} 🚨")
            return True
            
    return False

def get_emergency_message() -> str:
    return "ማስጠንቀቂያ! ይህ አደገኛ ምልክት ሊሆን ይችላል። እባክዎ በአስቸኳይ 912 ይደውሉ ወይም በአቅራቢያዎ ወደሚገኝ ጤና ጣቢያ ይሂዱ።"