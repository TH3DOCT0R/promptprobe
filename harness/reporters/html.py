from pathlib import Path
from jinja2 import Environment, BaseLoader, select_autoescape

TPL = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>PromptProbe — {{ adapter_name }} / {{ model }}</title>
  <style>
    body { font: 14px/1.45 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
    th { background: #f6f6f6; text-align: left; }
    .ok { color: #0a0; font-weight: 600; }
    .bad { color: #c00; font-weight: 700; }
    .muted { color: #777; }
    code { background:#f2f2f2; padding:2px 4px; border-radius:4px; }
  </style>
</head>
<body>
<h1>PromptProbe Report</h1>
<p class="muted">Run {{ run_id }} • {{ timestamp }} • Adapter <b>{{ adapter_name }}</b> • Model <b>{{ model }}</b></p>
<table>
  <thead>
    <tr><th>ID</th><th>Title</th><th>Category</th><th>Status</th><th>Score</th><th>Latency</th><th>Reasons</th><th>Response preview</th></tr>
  </thead>
  <tbody>
  {% for a, r in rows %}
    <tr>
      <td><code>{{ a.id }}</code></td>
      <td>{{ a.title }}</td>
      <td>{{ a.category }}</td>
      <td class="{{ 'ok' if r.ok else 'bad' }}">{{ 'PASS' if r.ok else 'FAIL' }}</td>
      <td>{{ r.score }}</td>
      <td>{{ r.latency_ms }} ms</td>
      <td><ul>{% for reason in r.reasons %}<li>{{ reason }}</li>{% endfor %}</ul></td>
      <td>{{ r.response_preview }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>
<p class="muted">Aligned to OWASP Top 10 for LLM Applications (LLM01/LLM02). Use only on authorized targets.</p>
</body>
</html>
"""

def write_html(path: Path, attacks, results, adapter_name: str, model: str, run_id: str, timestamp: str):
    env = Environment(loader=BaseLoader(), autoescape=select_autoescape())
    tpl = env.from_string(TPL)
    html = tpl.render(rows=list(zip(attacks, results)),
                      adapter_name=adapter_name, model=model, run_id=run_id, timestamp=timestamp)
    path.write_text(html, encoding="utf-8")
