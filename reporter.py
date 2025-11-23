# reporter.py
class Reporter:
    def __init__(self, html_out: Optional[str]=None):
        self.findings = []
        
    def add_finding(self, item: dict):
        self.findings.append(item)

    def write_terminal(self, findings): 
        for f in findings:
            print(f"- URL: {f['url']}")
            print(f"  Param: {f['param']}")
            print(f"  Payload: {f['payload']}")
            print(f"  Detected as: {f['detected_context']}")
            snippet = f.get('snippet','') or ''
            print(f"  Snippet: {snippet[:200].replace(chr(10),' ')}")
            print("-" * 40)


    def write_html(self, out='report.html', findings): 
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