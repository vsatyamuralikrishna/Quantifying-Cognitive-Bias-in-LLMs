import platform
from typing import List, Dict, Any
from qcbai.llm.base import ModelRunner
from pathlib import Path
import yaml
import ollama  # ✅ Requires `pip install ollama`

# Load YAML config from the same directory
MODEL_CONFIG_PATH = Path(__file__).parent / "models.yaml"


class OllamaModel(ModelRunner):
    """
    Model runner that uses the Ollama Python client directly (no server call).
    """

    def __init__(self, name: str, slug: str, temperature: float = 0.7):
        self.name = name
        self.slug = slug
        self.temperature = temperature

    def get_name(self) -> str:
        return self.name

    def get_slug(self) -> str:
        return self.slug

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature
        }

    def run_prompt(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """
        Runs prompt using the Ollama Python client.
        """
        try:
            response = ollama.chat(
                model=self.name,
                messages=messages,
                options={"temperature": temperature}
            )
            return {
                "text": response.get("message", {}).get("content", ""),
                "raw": response
            }
        except Exception as e:
            return {
                "text": "",
                "error": str(e)
            }


def detect_gpu_backend() -> str:
    system = platform.system()
    if system == "Darwin":
        return "Metal (Apple Silicon)"
    elif system == "Linux":
        return "CUDA (NVIDIA GPU)"
    else:
        return "CPU fallback or unknown system"


def load_ollama_model_configs() -> List[OllamaModel]:
    """
    Parses `models.yaml` and returns a list of OllamaModel instances.
    """
    if not MODEL_CONFIG_PATH.exists():
        print(f"⚠️ Model config not found at {MODEL_CONFIG_PATH}")
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
        else:
            print(f"⚠️ Invalid config entry: {entry}")

    return runners


# Exported constant used in registry
OLLAMA_MODELS: List[ModelRunner] = load_ollama_model_configs()