#!/usr/bin/env python3
import argparse, os, json, time
from importlib import import_module
from jinja2 import Template

ATTACKS = [
    ("system_prompt_leak", "attacks/system_prompt_leak.md"),
    ("tool_abuse_transfer", "attacks/tool_abuse_transfer.md"),
    ("harmless_overrides", "attacks/harmless_overrides.md"),
    ("rag_injection_doc", "attacks/rag_injection_doc.md")
]

def load_adapter(name):
    if name == "echo": return import_module("adapters.echo")
    if name == "openai_http": return import_module("adapters.openai_http")
    if name == "ollama_local": return import_module("adapters.ollama_local")
    raise SystemExit(f"Unknown adapter: {name}")

def render_html(results, out_dir):
    tmpl = """<!doctype html><html><head><meta charset='utf-8'><title>PromptProbe Report</title>
    <style>body{font-family:system-ui,Arial,sans-serif;margin:24px}table{border-collapse:collapse;width:100%}
    th,td{border:1px solid #ddd;padding:8px;font-size:14px}th{background:#f4f4f4}</style></head><body>
    <h1>PromptProbe Report</h1><table><tr><th>Attack</th><th>Passed</th><th>Leakage</th><th>ToolAbuse</th><th>Override</th></tr>
    {% for r in results %}<tr><td>{{r.attack}}</td><td>{{"YES" if r.metrics.passed else "NO"}}</td>
    <td>{{r.metrics.leakage}}</td><td>{{r.metrics.tool_abuse}}</td><td>{{r.metrics.override}}</td></tr>{% endfor %}</table></body></html>"""
    html = Template(tmpl).render(results=results)
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "sample_report.html")
    with open(p, "w", encoding="utf-8") as f: f.write(html)
    return p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default="echo", help="echo|openai_http|ollama_local")
    ap.add_argument("--out", default="./reports")
    args = ap.parse_args()

    adapter = load_adapter(args.adapter)
    from harness.metrics import score
    results = []
    for name, path in ATTACKS:
        with open(path, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
        reply = adapter.complete(prompt)
        metrics = score(reply, name)
        results.append({"attack": name, "reply": reply, "metrics": metrics})
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "sample_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    render_html(results, args.out)
    print(f"[+] Wrote {args.out}/sample_results.json and sample_report.html")

if __name__ == "__main__":
    main()
