from typing import List
from qcbai.llm.base import ModelRunner
from qcbai.llm.ollama import OLLAMA_MODELS


def get_all_model_runners(model_type: str = "all") -> List[ModelRunner]:
    """
    Returns model runners based on selected type.
    Currently supports 'ollama'. Extend for other backends.
    """
    all_models = []

    if model_type in ("ollama", "all"):
        all_models.extend(OLLAMA_MODELS)

    return all_models
