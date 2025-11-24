from bs4 import BeautifulSoup
from typing import Optional, Dict
import html as _html


def _short(s: str, n: int = 200) -> str:
    if not s:
        return ""
    s = s.strip()
    return (s[:n] + "...") if len(s) > n else s


def detect_reflection(response_text: str, token: str) -> Optional[Dict]:
    if not response_text or not token:
        return None

    escaped_token = _html.escape(token)
    if token not in response_text and escaped_token not in response_text:
        return None

    soup = BeautifulSoup(response_text, "html.parser")

    token_l = token.lower()

    # 1) attribute-name 
    for el in soup.find_all():
        # el.attrs keys are attribute names; iterate them
        for attr_name in (el.attrs.keys() if el.attrs else []):
            if attr_name and token_l in str(attr_name).lower():
                return {"context": "attribute-name", "snippet": _short(str(el))}

    # 2) attribute-value
    for el in soup.find_all():
        if not el.attrs:
            continue
        for val in el.attrs.values():
            try:
                if isinstance(val, list):
                    joined = " ".join(val)
                    if token in joined or escaped_token in joined:
                        return {"context": "attribute-value", "snippet": _short(str(el))}
                else:
                    if token in str(val) or escaped_token in str(val):
                        return {"context": "attribute-value", "snippet": _short(str(el))}
            except Exception:
                continue

    # 3) script content
    for s in soup.find_all("script"):
        script_text = s.string or ""
        if script_text and (token in script_text or escaped_token in script_text):
            return {"context": "script", "snippet": _short(script_text)}

    # 4) text-node fallback
    full_text = soup.get_text(separator=" ", strip=True)
    if token in full_text or escaped_token in full_text:
        return {"context": "text-node", "snippet": _short(full_text)}

    return None
