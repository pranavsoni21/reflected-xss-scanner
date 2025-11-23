# local_test_app.py
"""
Tiny Flask app to test the Reflected XSS scanner.
Do NOT run this on a public server. For local testing only.

Endpoints:
  GET /reflect_attr_name?PAYLD_xxx=1
    - Reflects the *parameter NAMES* as attribute names in the returned HTML.

  GET /reflect_attr_value?q=PAYLD_xxx
    - Reflects parameter values inside attribute values.

  GET /reflect_text?q=PAYLD_xxx
    - Reflects parameter values inside normal text nodes.

  GET /reflect_script?q=PAYLD_xxx
    - Reflects parameter values inside a <script> block.

  GET /reflect_all?q=...&PAYLD_xxx=1
    - Shows all contexts on one page (useful for quick testing).
"""
from flask import Flask, request, Response
from markupsafe import Markup

app = Flask(__name__)


@app.route('/')
def index():
    return """
    <h2>Local XSS Test App</h2>
    <ul>
      <li>/reflect_attr_name?PAYLD_token=1</li>
      <li>/reflect_attr_value?q=PAYLD_token</li>
      <li>/reflect_text?q=PAYLD_token</li>
      <li>/reflect_script?q=PAYLD_token</li>
      <li>/reflect_all?q=PAYLD_token&PAYLD_token=1</li>
    </ul>
    <p>Use the scanner against these endpoints.</p>
    """


@app.route('/reflect_attr_name')
def reflect_attr_name():
    """
    Build HTML where parameter NAMES are used as attribute names.
    Example output (if query contains ?PAYLD_abc=1):
      <div PAYLD_abc="1">Attribute-name test</div>
    """
    # Danger: intentionally rendering attribute names without escaping to simulate vulnerable app.
    parts = []
    for key, val in request.args.items():
        # create a tag that has the param name as attribute name
        # e.g., <div PAYLD_abc="1">... </div>
        parts.append(f'<div {key}="{val}">Reflected attribute-name: {key}={val}</div>')
    body = "<h3>Attribute-name reflections</h3>" + "".join(parts)
    return Response(body, mimetype='text/html')


@app.route('/reflect_attr_value')
def reflect_attr_value():
    """
    Reflect parameter values inside attribute values.
    Example:
      <img alt="...value..." src="/static/pixel.png">
    """
    parts = []
    # For each param, render an element where the value goes inside attribute
    for key, val in request.args.items():
        # intentionally not escaping the value inside attribute to mimic a vulnerable server
        parts.append(f'<div data-{key}="{val}">Reflected attribute-value for param {key}</div>')
    body = "<h3>Attribute-value reflections</h3>" + "".join(parts)
    return Response(body, mimetype='text/html')


@app.route('/reflect_text')
def reflect_text():
    """
    Reflect parameter values into text nodes.
    """
    parts = []
    for key, val in request.args.items():
        parts.append(f'<p>Param <b>{key}</b> reflected in text: {val}</p>')
    body = "<h3>Text node reflections</h3>" + "".join(parts)
    return Response(body, mimetype='text/html')


@app.route('/reflect_script')
def reflect_script():
    """
    Reflect parameter values inside a <script> block.
    """
    # Join all params into a JS variable to simulate JS context reflection
    js_pairs = []
    for key, val in request.args.items():
        # intentionally not escaping to simulate vulnerable behavior
        js_pairs.append(f'  "{key}": "{val}"')
    js_obj = "{\n" + ",\n".join(js_pairs) + "\n}"
    body = f"""
    <h3>Script reflections</h3>
    <script>
    // This script contains reflected values (vulnerable simulation)
    var REFLECTED = {js_obj};
    console.log('REFLECTED', REFLECTED);
    </script>
    <p>Look at browser console or page source for reflected values.</p>
    """
    return Response(body, mimetype='text/html')


@app.route('/reflect_all')
def reflect_all():
    """
    Single page showing all contexts together for quick testing.
    """
    name_parts = []
    value_parts = []
    text_parts = []
    for key, val in request.args.items():
        name_parts.append(f'<div {key}="{val}">attr-name -> {key}={val}</div>')
        value_parts.append(f'<div data-{key}="{val}">attr-value -> {key}={val}</div>')
        text_parts.append(f'<p>text -> {key} = {val}</p>')

    # script part
    js_pairs = []
    for key, val in request.args.items():
        js_pairs.append(f'  "{key}": "{val}"')
    js_obj = "{\n" + ",\n".join(js_pairs) + "\n}"

    body = f"""
    <h2>All reflection contexts</h2>
    <section>
      <h3>Attribute-name</h3>
      {''.join(name_parts)}
    </section>
    <section>
      <h3>Attribute-value</h3>
      {''.join(value_parts)}
    </section>
    <section>
      <h3>Text nodes</h3>
      {''.join(text_parts)}
    </section>
    <section>
      <h3>Script</h3>
      <script>
        var REF = {js_obj};
        console.log('REF:', REF);
      </script>
    </section>
    """
    # Use Markup to ensure the assembled HTML is returned as-is
    return Response(Markup(body), mimetype='text/html')


if __name__ == '__main__':
    # Run in debug mode for easier local testing
    print("Starting local XSS test app on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
