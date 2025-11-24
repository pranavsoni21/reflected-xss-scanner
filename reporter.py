from typing import List, Dict
import html


class Reporter:
    def __init__(self):
        self.findings: List[Dict] = []

    def add(self, finding: Dict):
        self.findings.append(finding)

    def terminal(self):
        if not self.findings:
            print("No reflections found.")
            return

        print("\n=== Reflected XSS Findings ===")
        for f in self.findings:
            print("----------------------------")
            print(f"URL: {f['url']}")
            print(f"Param: {f['param']}")
            print(f"Payload: {f['payload']}")
            print(f"Context: {f['context']}")
            print(f"Snippet: {f['snippet']}")
        print("----------------------------")

    def html(self, outpath="report.html"):
        rows = ""
        for f in self.findings:
            rows += f"""
            <tr>
              <td>{html.escape(f['url'])}</td>
              <td>{html.escape(f['param'])}</td>
              <td>{html.escape(f['payload'])}</td>
              <td>{html.escape(f['context'])}</td>
              <td><pre>{html.escape(f['snippet'])}</pre></td>
            </tr>
            """

        doc = f"""
        <html><body>
        <h2>Reflected XSS Report</h2>
        <table border="1" cellpadding="5" cellspacing="0">
          <tr>
            <th>URL</th>
            <th>Param</th>
            <th>Payload</th>
            <th>Context</th>
            <th>Snippet</th>
          </tr>
          {rows}
        </table>
        </body></html>
        """

        with open(outpath, "w", encoding="utf-8") as f:
            f.write(doc)

        print(f"[+] HTML report saved to {outpath}")
