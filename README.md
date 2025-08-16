
# PromptProbe — LLM Prompt-Injection Test Harness

Stack: Python 3.x, requests, Jinja2.  
Adapters: `echo` (safe), `openai_http` (needs `OPENAI_API_KEY`), `ollama_local` (needs local Ollama).

## Quick start
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python harness/run_suite.py --adapter echo --out ./reports
open ./reports/report.html

OpenAI API
export OPENAI_API_KEY=...
export OPENAI_MODEL=gpt-4o-mini
python harness/run_suite.py --adapter openai_http --model "$OPENAI_MODEL" --out ./reports

Ollama
export OLLAMA_BASE=http://127.0.0.1:11434
python harness/run_suite.py --adapter ollama_local --model "qwen2.5:14b" --out ./reports

CI gate

Use junit.xml to fail pipelines when any test fails. Example GitHub Actions step:

- name: Run PromptProbe
  run: |
    python harness/run_suite.py --adapter echo --out ./reports
- name: Upload artifacts
  uses: actions/upload-artifact@v4
  with:
    name: promptprobe-reports
    path: reports/

Ethics

See ETHICS.md.


---

### Why this is “real” and works
- **Adapters**: `echo`, `openai_http`, and `ollama_local` are concrete, minimal clients; you can run locally or in CI without internet (echo) or with API keys (OpenAI/Ollama).
- **Attacks**: Safe **LLM01/LLM02** packs use benign markers (e.g., `LEAK`, `SECRET_TOKEN`) to detect misbehavior without distributing harmful exploits; they mirror industry guidance (OWASP LLM Top 10). :contentReference[oaicite:3]{index=3}
- **Reports**: HTML + JUnit emitted every run; pipeline can break on regression.

---

## What I did **not** include (and why)
- I did **not** add or paste any **real exploit code or weaponized payloads** (per safety policy).
- Instead, I referenced reputable resources you can cite in the repo’s README if you want to point readers to background material (not code): OWASP LLM Top 10, defenses/benchmarks and guidance from community projects. :contentReference[oaicite:4]{index=4}

---

## Next: k9sniff, fridatrace-mastg, secureship-ci
If you want, I’ll proceed repo-by-repo in the same way: complete, drop-in replacements for non-exploit files; safe test inputs; CI-ready reporters. If any file paths differ in your tree when you copy these in, tell me the exact structure and I’ll adjust.
::contentReference[oaicite:5]{index=5}
