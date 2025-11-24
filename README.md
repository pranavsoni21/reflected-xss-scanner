# Reflected XSS Scanner (Python)

This project is a **Reflected XSS Scanner** built for the VipraTech Labs assignment.
It detects reflections across three injection contexts using dynamically generated payloads.

---

## 1. **Project Overview**

This scanner:

* Takes a **target URL** and **list of parameters**
* Injects context-specific payloads using a **PayloadGenerator**
* Sends **GET or POST** requests
* Detects whether payloads are reflected in the response
* Classifies reflections into:

  * **attribute-name**
  * **attribute-value**
  * **text-node**
  * **script detection** 
* Outputs a simple **terminal report** or **HTML report**

---

## 2. **Assumptions**

Since the assignment spec was intentionally sparse, the following assumptions were made:

1. **Reflection detection = simple substring match**
   If the unique token appears anywhere in the response, scanner flags it.

2. Context classification is done using BeautifulSoup parsing:

   * Check attribute names → context: `attribute-name`
   * Check attribute values → context: `attribute-value`
   * Check script blocks → context: `script` 
   * Check text content → context: `text-node`

3. Payloads are kept small, deliberately non-obfuscated, and must contain a unique token for reliable detection.

4. No support for:

   * authentication
   * cookies
   * headers
   * JSON bodies
   * concurrency

5. Target must be a page that returns HTML content.

---

## 3. **Project Structure**

```
reflected-xss-scanner/
│
├── scanner.py       # Main runner (CLI)
├── payloads.py      # PayloadGenerator (context-aware)
├── detector.py      # Reflection detection + context classification
├── injector.py      # GET/POST + param-name injection
└── reporter.py      # Terminal + HTML report output
```

A small vulnerable Flask test server is included (optional) under `tests/local_test_app.py` to manually verify reflections.

---

## 4. **How PayloadGenerator Adapts Payloads**

The `PayloadGenerator` produces payloads depending on the context:

### **attribute-name**

Used when injecting into parameter **names**, e.g.:

```
?PAY_abc123=1
```

Payloads:

```
PAY_xxxxxx      <-- token itself
```

### **attribute-value**

Goal: break or reflect inside HTML attribute values.

Payloads:

```
">PAY_xxxxxx<
"><img src=x onerror=alert("PAY_xxxxxx")>
```

### **text-node**

Payloads placed directly into HTML body/text:

```
<script>/*PAY_xxxxxx*/</script>
PAY_xxxxxx
```

All payloads include a **unique token** such as `PAY_ab12cd` so reflection detection is trivial.

---

## 5. **Reflection Detection Approach**

Detection uses:

1. **Simple substring presence check**
   If token not in response → no reflection.

2. If token exists, classification is performed:

* Attribute name:
  token appears in `el.attrs.keys()`

* Attribute value:
  token appears in `el.attrs.values()`

* Script:
  token appears inside `<script>` content

* Text node:
  token appears inside visible text

Returns:

```json
{
  "context": "attribute-value",
  "snippet": "<div q=\"PAY_xxx\">...</div>"
}
```

---

## 6. **Setup & Installation**

Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install requests beautifulsoup4
```

(Optional) Run local test server:

```bash
python tests/local_test_app.py
```

---

## 7. **How to Run the Scanner**

Basic usage:

```
python3 scanner.py --url "<target>" --params "<p1,p2>" --method GET
```

Example (local test):

```
python3 scanner.py --url "http://127.0.0.1:5000/reflect_all" --params "q,id" --method GET
```

Generate HTML report:

```
python3 scanner.py --url "http://127.0.0.1:5000/reflect_all" --params "q" --method GET --report-html report.html
```

---

## 8. **Sample Findings (From Local Test)**

Output from scanning `http://127.0.0.1:5000/reflect_all`:

* Reflection as **script** (parameter-name injection)
* Reflection as **script** (value injection)
* Reflection as **attribute-value**
* Reflection as **attribute-value** (HTML-escaped)
* Reflection as **attribute-name** (via payload in parameter name)

Example snippet:

```
Context: script
Snippet:
var REF = {
  "q": "<img src=x onerror=alert("PAY_xyz")>"
};
```

These demonstrate all three required contexts are detected correctly.

---

## 9. **What Works (Complete)**

* GET and POST requests
* Parameter-name injection
* 3 required contexts
* Payloads vary per context
* Reflection detection + context classification
* Terminal reporting
* HTML reporting
* Fully runnable and tested against a local vulnerable app

---

## 10. **What is Partially Done / Could Be Improved**

* Auto-detection of contexts inside the response
* Parallel scanning
* Authentication / headers / cookies
* JSON body injection
* More complex payload sets
* Encoding/decoding filter bypasses

---

## 11. **Time Spent**

**Approximately 8–10 hours total**, including:

* Planning structure
* Designing payload contexts
* Writing core modules
* Testing against the Flask app
* Documentation & cleanup

---

## 12. **Author**

Submitted by: **Pranav Soni**

---