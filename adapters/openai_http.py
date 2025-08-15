import os, requests


def complete(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    base = os.getenv("OPENAI_BASE", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        return "[OPENAI] missing OPENAI_API_KEY"
    url = f"{base}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages":[{"role":"user", "content": prompt}], "temperature":0}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[OPENAI ERROR] {e}"
