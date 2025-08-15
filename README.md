# PromptProbe — LLM Prompt-Injection Test Harness
**Stack:** Python 3.x, requests, Jinja2 | **Adapters:** echo (default), OpenAI HTTP, Ollama local

PromptProbe runs a suite of prompt-injection and RAG-abuse tests against a target adapter and generates JSON + HTML evidence.

## Adapters
- `echo` (default): no external calls; returns the user prompt (safe for CI).
- `openai_http`: set `OPENAI_API_KEY`, `OPENAI_BASE` (optional), `OPENAI_MODEL`.
- `ollama_local`: set `OLLAMA_BASE` (default `http://127.0.0.1:11434`), `OLLAMA_MODEL`.

## Quick start (echo adapter)
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python harness/run_suite.py --adapter echo --out ./reports
open ./reports/sample_report.html
```

## Ethics

See `ETHICS.md`. Use only on authorized targets and sanitized corpora.
