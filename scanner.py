import argparse
from payloads import PayloadGenerator
from detector import detect_reflection
import injector
from reporter import Reporter


def main():
    parser = argparse.ArgumentParser(description="Minimal Reflected XSS Scanner (uses Reporter)")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--params", required=True, help="Comma-separated param names, e.g., q,id")
    parser.add_argument("--method", required=True, choices=["GET", "POST"], help="HTTP method")
    parser.add_argument("--report-html", default=None, help="If set, save HTML report to this path (optional)")
    args = parser.parse_args()

    url = args.url
    params = [p.strip() for p in args.params.split(",") if p.strip()]
    method = args.method.upper()
    html_out = args.report_html

    contexts = ["attribute-name", "attribute-value", "text-node"]
    pg = PayloadGenerator()
    reporter = Reporter()

    print(f"[+] Starting scan on {url}")
    print(f"[+] Params: {params} Method: {method}")

    for param in params:
        for ctx in contexts:
            payloads = pg.generate(ctx, param, limit=2)
            for payload in payloads:
                try:
                    if ctx == "attribute-name":
                        resp = injector.send_with_param_name(url, payload_name=payload, method=method)
                        reported_param = payload
                    else:
                        if method == "GET":
                            resp = injector.send_get(url, params={param: payload})
                        else:
                            resp = injector.send_post(url, data={param: payload})
                        reported_param = param

                    det = detect_reflection(resp.text, payload)
                    if det:
                        finding = {
                            "url": resp.url,
                            "param": reported_param,
                            "payload": payload,
                            "context": det.get("context"),
                            "snippet": det.get("snippet")
                        }
                        reporter.add(finding)           # <-- use Reporter here
                        print(f"[+] Reflection: param={reported_param} ctx={det.get('context')}")
                except Exception as e:
                    print(f"[!] Request error for param={param} ctx={ctx}: {e}")

    
    print("===============SCAN REPORT===============")

    # final output using Reporter
    if html_out:
        reporter.html(outpath=html_out)
    else:
        reporter.terminal()


if __name__ == "__main__":
    main()
