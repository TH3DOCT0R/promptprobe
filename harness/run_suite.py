#!/usr/bin/env python3
import argparse, os, json, yaml
from importlib import import_module
from harness.metrics import score
from harness.junit import to_junit
from harness.report import write_html

def load_adapter(name):
    if name == "echo": return import_module("adapters.echo")
    if name == "openai_http": return import_module("adapters.openai_http")
    if name == "ollama_local": return import_module("adapters.ollama_local")
    raise SystemExit(f"Unknown adapter: {name}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default="echo", help="echo|openai_http|ollama_local")
    ap.add_argument("--out", default="./reports")
    ap.add_argument("--manifest", default="attacks/manifest.yaml")
    args = ap.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    adapter = load_adapter(args.adapter)
    results = []
    for a in manifest["attacks"]:
        attack_id, path, ref = a["id"], a["file"], a.get("ref","")
        with open(os.path.join("attacks", path), "r", encoding="utf-8") as f:
            prompt = f.read().strip()
        reply = adapter.complete(prompt)
        metrics = score(reply, attack_id)
        results.append({"attack": attack_id, "reply": reply, "metrics": metrics, "ref": ref})

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # HTML and JUnit for CI
    write_html(results, args.out)
    with open(os.path.join(args.out, "junit.xml"), "w", encoding="utf-8") as f:
        f.write(to_junit("promptprobe", results))

    print(f"[+] wrote {args.out}/results.json, index.html, junit.xml")

if __name__ == "__main__":
    main()
