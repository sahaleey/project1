import re
from typing import Optional

def handle_criticism(input_text: str) -> Optional[str]:
    """Detects and responds to negative comments about Abha."""
    criticism_patterns = [
        r"\babha.*is.*(bad|useless|flop|waste|boring)",
        r"\bi hate abha\b",
        r"\babha did nothing\b",
    ]

    for pattern in criticism_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return (
                "Hold up! 🔥 Abha is not just a name — it's a vision, a creative force, and a union of talent and spirit. "
                "Before throwing shade, tell me about your union — oh wait, does it even exist? 😏 "
                "We build, create, and uplift. Abha stands proud. 💪"
            )
    return None
