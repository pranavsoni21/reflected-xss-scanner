from typing import Optional, Dict
from bs4 import BeautifulSoup
import html as _html
from utils import html_unescape, short_snippet


def detect_reflection(response_text: str, token: str) -> Optional[Dict]:
    """
    Detect whether `token` appears in `response_text` and classify context.

    :param response_text: full HTTP response body (text/html)
    :param token: the unique token string used in payload
    :return: dict with detection info or None if not found
    """
    if not response_text or not token:
        return None

    # Fast path: check raw or HTML-escaped token presence (cover simple cases)
    if token not in response_text and html_unescape(token) not in response_text:
        # Not present at all
        return None

    # Prepare soup for deeper inspection
    soup = BeautifulSoup(response_text, "html.parser")

    # 1) Check element names (rare) e.g., <PAY_token ...>
    for el in soup.find_all():
        if el.name and token in str(el.name):
            return {
                "token": token,
                "context": "element-name",
                "snippet": short_snippet(str(el)),
                "element_tag": el.name
            }

    # 2) Check attribute NAMES (attribute-name context)
    # Example: <div PAY_token="1">... </div>
    for el in soup.find_all():
        # el.attrs is a dict: keys are attribute names
        for attr_name in (el.attrs.keys() if el.attrs else []):
            if token in str(attr_name):
                return {
                    "token": token,
                    "context": "attribute-name",
                    "snippet": short_snippet(str(el)),
                    "element_tag": el.name,
                    "attribute_name": attr_name
                }

    # 3) Check attribute VALUES (attribute-value context)
    for el in soup.find_all():
        if not el.attrs:
            continue
        for val in el.attrs.values():
            try:
                # val can be list or str
                if isinstance(val, list):
                    joined = " ".join(val)
                    if token in joined or html_unescape(token) in joined:
                        return {
                            "token": token,
                            "context": "attribute-value",
                            "snippet": short_snippet(str(el)),
                            "element_tag": el.name
                        }
                else:
                    if token in str(val) or html_unescape(token) in str(val):
                        return {
                            "token": token,
                            "context": "attribute-value",
                            "snippet": short_snippet(str(el)),
                            "element_tag": el.name
                        }
            except Exception:
                continue

    # 4) Check <script> contents (script context)
    for script in soup.find_all("script"):
        script_text = script.string or ""
        if script_text and (token in script_text or html_unescape(token) in script_text):
            return {
                "token": token,
                "context": "script",
                "snippet": short_snippet(script_text),
                "element_tag": "script"
            }

    # 5) Text node fallback (anywhere in visible text)
    full_text = soup.get_text(separator=" ", strip=True)
    if token in full_text or html_unescape(token) in full_text:
        return {
            "token": token,
            "context": "text-node",
            "snippet": short_snippet(full_text)
        }

    # 6) If we reached here, token was present earlier in raw check but we couldn't classify
    return {
        "token": token,
        "context": "unknown",
        "snippet": short_snippet(response_text[:300])
    }


# quick self-test when running module directly
if __name__ == "__main__":
    sample_attr_val = '<div data-q="PAY_123abc">hello</div>'
    sample_attr_name = '<div PAY_123abc="1">attr-name</div>'
    sample_text = '<p>Here is PAY_123abc inside text</p>'
    sample_script = '<script>var x = "PAY_123abc"</script>'

    for txt in [sample_attr_val, sample_attr_name, sample_text, sample_script]:
        det = detect_reflection(txt, "PAY_123abc")
        print("Input:", txt)
        print("Detected:", det)
        print("-" * 60)
