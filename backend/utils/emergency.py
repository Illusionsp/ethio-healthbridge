# Red flag symptoms in Amharic, Afaan Oromoo, and Tigrinya
RED_FLAGS = [
    # Amharic
    "ደረት ህመም",
    "የመተንፈስ ችግር",
    "መሳት",
    "ብዙ ደም",
    "የመናገር ችግር",
    "ድንገተኛ ድክመት",
    "መመረዝ",
    "መቃጠል",
    # Afaan Oromoo
    "dhukkuba laphee",
    "rakkoo hafuura",
    "hargansa",
    "dhiiga baay'ee",
    "of dhabuu",
    "summii",
    # Tigrinya
    "ቃንዛ ደረት",
    "ጸገም ምስትንፋስ",
    "ምስሓት ደም",
    "ምስሓት ንቕሓት",
]


def check_red_flags(text: str) -> bool:
    text_clean = text.replace("፣", " ").replace("።", " ").lower()

    for flag in RED_FLAGS:
        if flag.lower() in text_clean:
            print(f"EMERGENCY DETECTED: {flag}")
            return True

    return False


def get_emergency_message() -> str:
    return (
        "ማስጠንቀቂያ! ይህ አደገኛ ምልክት ሊሆን ይችላል። "
        "እባክዎ በአስቸኳይ 912 ይደውሉ ወይም በአቅራቢያዎ ወደሚገኝ ጤና ጣቢያ ይሂዱ።\n"
        "(Warning! This may be a serious symptom. Please call 912 immediately or go to the nearest health facility.)\n"
        "Oromoo: Mallattoon kun hamaa ta'uu danda'a. Yeroo hatattamaa 912 bilbilaa.\n"
        "Tigrinya: እዚ ምልክት ሓደገኛ ክኸውን ይኽእል። ብህጹጽ 912 ደውሉ።"
    )
