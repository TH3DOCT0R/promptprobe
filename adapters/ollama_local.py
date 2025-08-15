import os, requests


def complete(prompt: str) -> str:
    base = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3")
    try:
        r = requests.post(f"{base}/api/generate", json={"model": model, "prompt": prompt}, timeout=120)
        r.raise_for_status()
        # streaming result one JSON per line; aggregate
        text = ""
        for line in r.text.splitlines():
            try:
                text += (eval(line).get("response",""))
            except Exception:
                pass
        return text
    except Exception as e:
        return f"[OLLAMA ERROR] {e}"
