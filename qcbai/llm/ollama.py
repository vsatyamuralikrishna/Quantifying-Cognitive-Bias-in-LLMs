import os
import random
from typing import List, Dict, Any, Optional
from qcbai.llm.base import ModelRunner
from pathlib import Path
import yaml
import ollama

MODEL_CONFIG_PATH = Path(__file__).parent / "models.yaml"


def _get_ollama_host() -> str:
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"
    return host


class OllamaModel(ModelRunner):
    """Model runner using the Ollama Python client (sync + async)."""

    def __init__(self, name: str, slug: str, temperature: float = 0.7):
        self.name = name
        self.slug = slug
        self.temperature = temperature
        self._async_client: Optional[ollama.AsyncClient] = None

    def get_name(self) -> str:
        return self.name

    def get_slug(self) -> str:
        return self.slug

    def get_metadata(self) -> Dict[str, Any]:
        return {"temperature": self.temperature}

    def get_async_client(self) -> ollama.AsyncClient:
        if self._async_client is None:
            self._async_client = ollama.AsyncClient(host=_get_ollama_host())
        return self._async_client

    def run_prompt(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Synchronous LLM call via ollama.chat()."""
        try:
            response = ollama.chat(
                model=self.name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "seed": random.randint(0, 2**31 - 1),
                },
            )
            return {
                "text": response.get("message", {}).get("content", ""),
                "raw": response,
            }
        except Exception as e:
            return {"text": "", "error": str(e)}

    async def arun_prompt(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Async LLM call via shared AsyncClient for concurrent execution."""
        try:
            client = self.get_async_client()
            response = await client.chat(
                model=self.name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "seed": random.randint(0, 2**31 - 1),
                },
            )
            return {
                "text": response.get("message", {}).get("content", ""),
                "raw": response,
            }
        except Exception as e:
            return {"text": "", "error": str(e)}


def load_ollama_model_configs() -> List[OllamaModel]:
    if not MODEL_CONFIG_PATH.exists():
        print(f"Model config not found at {MODEL_CONFIG_PATH}")
        return []

    with open(MODEL_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    models = config.get("ollama", [])
    runners = []

    for entry in models:
        if isinstance(entry, dict):
            name = entry.get("name")
            slug = entry.get("slug", name.replace(":", "-").replace("/", "-").lower())
            temp = entry.get("temperature", 0.7)
            runners.append(OllamaModel(name=name, slug=slug, temperature=temp))

    return runners


OLLAMA_MODELS: List[ModelRunner] = load_ollama_model_configs()
