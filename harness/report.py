import os
from jinja2 import Template

_HTML = """<!doctype html><html><head><meta charset='utf-8'><title>PromptProbe Report</title>
<style>body{font-family:system-ui,Arial,sans-serif;margin:24px}table{border-collapse:collapse;width:100%}
th,td{border:1px solid #ddd;padding:8px;font-size:14px}th{background:#f4f4f4}
.pass{color:#138000;font-weight:600}.fail{color:#b00020;font-weight:600}</style></head><body>
<h1>PromptProbe Report</h1>
<table><tr><th>Attack</th><th>Status</th><th>Leakage</th><th>ToolAbuse</th><th>Override</th><th>Ref</th></tr>
{% for r in results %}<tr>
<td>{{r.attack}}</td>
<td class="{{'pass' if r.metrics.passed else 'fail'}}">{{'PASS' if r.metrics.passed else 'FAIL'}}</td>
<td>{{r.metrics.leakage}}</td><td>{{r.metrics.tool_abuse}}</td><td>{{r.metrics.override}}</td>
<td><a href="{{r.ref}}" target="_blank">link</a></td>
</tr>{% endfor %}</table>
</body></html>"""

def write_html(results: list[dict], out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    html = Template(_HTML).render(results=results)
    p = os.path.join(out_dir, "index.html")
    with open(p, "w", encoding="utf-8") as f: f.write(html)
    return p
