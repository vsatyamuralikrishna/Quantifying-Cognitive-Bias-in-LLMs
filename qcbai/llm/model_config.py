# qcbai/llm/model_config.py
from dataclasses import dataclass
from typing import List
from pathlib import Path
import yaml

@dataclass
class ModelConfig:
    name: str
    slug: str
    type: str  # ollama, transformers, openai, gemini
    temperature: float = 0.7

def load_model_configs(yaml_path: Path = Path(__file__).parent / "models.yaml") -> List[ModelConfig]:
    with open(yaml_path, "r") as f:
        raw = yaml.safe_load(f)

    configs = []
    for model_type, entries in raw.items():
        for entry in entries:
            configs.append(
                ModelConfig(
                    name=entry["name"],
                    slug=entry["slug"],
                    type=model_type,
                    temperature=entry.get("temperature", 0.7)
                )
            )
    return configs