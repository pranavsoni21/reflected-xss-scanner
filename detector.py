# detector.py
from typing import Optional, Dict

def detect_reflection(response_text: str, token: str) -> Optional[Dict]:
    # return {'context': 'attribute-value', 'snippet': '...'} or None
