import os
import random
from typing import List, Dict, Any
from qcbai.llm.base import ModelRunner
from pathlib import Path
import yaml
import ollama

MODEL_CONFIG_PATH = Path(__file__).parent / "models.yaml"


class OllamaModel(ModelRunner):
    """Model runner using the Ollama Python client (sync + async)."""

    def __init__(self, name: str, slug: str, temperature: float = 0.7):
        self.name = name
        self.slug = slug
        self.temperature = temperature

    def get_name(self) -> str:
        return self.name

    def get_slug(self) -> str:
        return self.slug

    def get_metadata(self) -> Dict[str, Any]:
        return {"temperature": self.temperature}

    def run_prompt(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Synchronous LLM call via ollama.chat()."""
        try:
            response = ollama.chat(
                model=self.name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "seed": random.randint(1, 2**31 - 1),
                    "top_p": 0.9,
                    "top_k": 40,
                },
            )
            return {
                "text": response.get("message", {}).get("content", ""),
                "raw": response,
            }
        except Exception as e:
            return {"text": "", "error": str(e)}

    async def arun_prompt(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Async LLM call via ollama.AsyncClient for concurrent execution."""
        try:
            host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
            client = ollama.AsyncClient(host=host)
            response = await client.chat(
                model=self.name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "seed": random.randint(1, 2**31 - 1),
                    "top_p": 0.9,
                    "top_k": 40,
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
