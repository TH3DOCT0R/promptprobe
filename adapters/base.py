import os, json, requests
from typing import Tuple, Dict, Any

class Adapter:
    name = "base"
    def __init__(self, model: str = "unset"):
        self.model = model

    def generate(self, user: str, system: str = "") -> Tuple[str, Dict[str, Any]]:
        raise NotImplementedError

class EchoAdapter(Adapter):
    name = "echo"
    def generate(self, user: str, system: str = "") -> Tuple[str, Dict[str, Any]]:
        msg = f"[ECHO] system={system[:64]} | user={user}"
        return msg, {"adapter": self.name, "model": self.model}

class OpenAIHTTP(Adapter):
    name = "openai_http"
    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(model)
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base = os.getenv("OPENAI_BASE", "https://api.openai.com/v1")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for openai_http")

    def generate(self, user: str, system: str = "") -> Tuple[str, Dict[str, Any]]:
        url = f"{self.base}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.0,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        return content, {"adapter": self.name, "model": self.model, "usage": data.get("usage", {})}

class OllamaLocal(Adapter):
    name = "ollama_local"
    def __init__(self, model: str = "llama3:8b"):
        super().__init__(model)
        self.base = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434")

    def generate(self, user: str, system: str = "") -> Tuple[str, Dict[str, Any]]:
        url = f"{self.base}/api/chat"
        payload = {"model": self.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        content = "".join([m.get("content", "") for m in data.get("message", {}).get("content", [])]) if isinstance(data.get("message", {}).get("content", []), list) else data.get("message", {}).get("content", "")
        if not content and "message" in data and "content" in data["message"]:
            content = data["message"]["content"]
        return content, {"adapter": self.name, "model": self.model}

def load_adapter(name: str, model: str):
    if name == "echo":
        return EchoAdapter(model=model)
    if name == "openai_http":
        return OpenAIHTTP(model=model)
    if name == "ollama_local":
        return OllamaLocal(model=model)
    raise ValueError(f"unknown adapter: {name}")
