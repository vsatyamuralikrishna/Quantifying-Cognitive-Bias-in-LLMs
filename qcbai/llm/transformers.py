# qcbai/llm/transformers.py

import os
import yaml
from pathlib import Path
from typing import List, Dict, Any

import torch
from transformers import pipeline
from qcbai.llm.base import ModelRunner

TRANSFORMER_CONFIG_PATH = Path(__file__).parent / "models.yaml"
SUPPORTED_TASK = "text-generation"


class TransformersModel(ModelRunner):
    """
    Adapter for HuggingFace models using the 'text-generation' pipeline,
    with automatic GPU support for CUDA or Metal backends.
    """

    def __init__(self, model_name: str, slug: str, temperature: float = 0.7):
        self.model_name = model_name
        self.slug = slug
        self.temperature = temperature
        self.pipeline = None

        device = self._get_device()

        try:
            print(f"Loading HF model: {model_name} on {device}")
            self.pipeline = pipeline(
                SUPPORTED_TASK,
                model=model_name,
                trust_remote_code=True,
                device=device  # GPU if available
            )
        except Exception as e:
            print(f"Failed to load HF model: {model_name} — {str(e)}")
            raise e

    def get_name(self) -> str:
        return self.slug

    def run_prompt(self, messages: List[Dict], temperature: float = 0.7) -> Dict[str, Any]:
        prompt = messages[0]["content"] if messages else ""

        try:
            results = self.pipeline(prompt, max_new_tokens=128, temperature=temperature, do_sample=True)
            full_text = results[0]["generated_text"]

            # Remove the original prompt from the result
            response_only = full_text[len(prompt):].strip()

            return {
                "text": response_only,
                "raw": results
            }
        except Exception as e:
            return {"text": "", "error": str(e)}

    @staticmethod
    def _get_device():
        """
        Returns the appropriate device:
        - CUDA: 0
        - MPS (Apple Silicon): 'mps'
        - CPU: -1
        """
        if torch.cuda.is_available():
            return 0
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return -1


def load_transformer_model_config() -> List[Dict]:
    if not TRANSFORMER_CONFIG_PATH.exists():
        print(f"HF config not found at {TRANSFORMER_CONFIG_PATH}")
        return []

    with open(TRANSFORMER_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    return config.get("transformers", [])


def get_transformer_models() -> List[ModelRunner]:
    configs = load_transformer_model_config()
    runners = []

    for entry in configs:
        model_name = entry["name"]
        slug = entry["slug"]
        temperature = entry.get("temperature", 0.7)

        try:
            runner = TransformersModel(model_name, slug, temperature)
            runners.append(runner)
        except Exception as e:
            print(f"Skipping model '{model_name}' due to error: {e}")

    return runners


TRANSFORMER_MODELS = get_transformer_models()