import httpx
import json
from typing import List, Dict, Optional, Any, Tuple
from backend.personas import SYSTEM_PROMPT

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1:latest"

# ─────────────────────────────────────────────────────────────────────────────
# SIMULATE_MODE = True   → instant pre-crafted responses, no Ollama required
# SIMULATE_MODE = False  → calls real Ollama at OLLAMA_URL
# ─────────────────────────────────────────────────────────────────────────────
SIMULATE_MODE = True


class LLMClient:
    def __init__(self, model: str = MODEL_NAME):
        self.model = model

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> str:
        if SIMULATE_MODE:
            from backend.simulated_client import simulate_response
            return await simulate_response(messages, system=system, model_override=model_override)

        # ── Real Ollama path ──────────────────────────────────────────────────
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        else:
            full_messages.append({"role": "system", "content": SYSTEM_PROMPT})
        full_messages.extend(messages)

        target_model = model_override if model_override else self.model
        payload = {
            "model": target_model,
            "messages": full_messages,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9},
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
            except httpx.HTTPError as e:
                return f"[Error calling model ({target_model}): {str(e)}]"
            except Exception as e:
                return f"[Unexpected error: {str(e)}]"

    async def get_status(self) -> Dict[str, Any]:
        if SIMULATE_MODE:
            return {
                "online": True,
                "simulated": True,
                "models": ["simulated-astrabot-v1"],
                "active_model": "simulated-astrabot-v1",
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(f"{OLLAMA_URL}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    active = (
                        self.model
                        if self.model in models or f"{self.model}:latest" in models
                        else (models[0] if models else self.model)
                    )
                    return {"online": True, "models": models, "active_model": active}
            except Exception as e:
                return {"online": False, "error": str(e), "active_model": self.model}
        return {"online": False, "error": "Unknown error", "active_model": self.model}

    async def close(self):
        pass


llm_client = LLMClient()