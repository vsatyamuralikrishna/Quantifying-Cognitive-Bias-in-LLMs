import os
import requests
import subprocess
import yaml
import platform
from typing import List, Dict, Any
from pathlib import Path
from qcbai.llm.base import ModelRunner

# Ollama server URL
OLLAMA_SERVER_URL = os.getenv("OLLAMA_SERVER_URL", "http://localhost:11434")

# Use the shared config file in llm/
MODEL_CONFIG_PATH = Path(__file__).parent / "models.yaml"


class OllamaModel(ModelRunner):
    """
    Adapter for running prompts through Ollama models hosted locally.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    def get_name(self) -> str:
        return self.model_name

    def run_prompt(self, messages: List[Dict], temperature: float = 0.7) -> Dict[str, Any]:
        url = f"{OLLAMA_SERVER_URL}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "text": data.get("message", {}).get("content", ""),
                "raw": data
            }
        except requests.exceptions.RequestException as e:
            return {
                "text": "",
                "error": str(e)
            }


def load_model_config() -> List[str]:
    """
    Loads Ollama model names from the unified models.yaml config.
    Supports structured entries with `name`, `slug`, and `temperature`.
    """
    if not MODEL_CONFIG_PATH.exists():
        print(f"⚠️ Model config not found at {MODEL_CONFIG_PATH}")
        return []

    with open(MODEL_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    models = config.get("ollama", [])

    model_names = []
    for entry in models:
        if isinstance(entry, dict) and "name" in entry:
            model_names.append(entry["name"])
        elif isinstance(entry, str):
            model_names.append(entry)
        else:
            print(f"⚠️ Skipping invalid Ollama model entry: {entry}")

    return model_names


def check_local_models() -> List[str]:
    """
    Queries the Ollama server for available local models.
    """
    try:
        response = requests.get(f"{OLLAMA_SERVER_URL}/api/tags")
        response.raise_for_status()
        return [model.get("name") for model in response.json().get("models", [])]
    except Exception as e:
        print(f"Could not fetch local Ollama models: {e}")
        return []


def pull_model(model_name: str) -> bool:
    """
    Pulls the model using `ollama pull`. Returns success status.
    """
    print(f"Pulling missing Ollama model: {model_name}")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to pull Ollama model: {model_name} — skipping.")
        return False
    return True


def detect_gpu_backend() -> str:
    """
    Detects the platform-specific backend Ollama is expected to use.
    """
    system = platform.system()
    if system == "Darwin":
        return "Metal (Apple Silicon)"
    elif system == "Linux":
        return "CUDA (NVIDIA GPU)"
    else:
        return "CPU fallback or unknown system"


def get_ollama_models() -> List[ModelRunner]:
    """
    Loads Ollama models from config, ensures they are available,
    and wraps them as ModelRunner instances.
    """
    backend = detect_gpu_backend()
    print(f"Ollama is expected to use: {backend}")

    config_models = load_model_config()
    local_models = check_local_models()

    runners = []
    for model_name in config_models:
        if model_name not in local_models:
            if not pull_model(model_name):
                continue
        runners.append(OllamaModel(model_name))

    return runners

def get_slug(self) -> str:
    return self.model_name.replace(":", "-").replace("/", "-").lower()


# Used by registry
OLLAMA_MODELS = get_ollama_models()