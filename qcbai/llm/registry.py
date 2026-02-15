from typing import List
from qcbai.llm.base import ModelRunner
from qcbai.llm.ollama import OLLAMA_MODELS

try:
    from qcbai.llm.vllm import VLLM_MODELS, VLLM_AVAILABLE
except ImportError:
    VLLM_MODELS = []
    VLLM_AVAILABLE = False


def get_all_model_runners(model_type: str = "all") -> List[ModelRunner]:
    """
    Returns model runners based on selected type.
    Supports 'ollama', 'vllm', or 'all'.
    """
    all_models = []

    if model_type in ("ollama", "all"):
        all_models.extend(OLLAMA_MODELS)

    if model_type in ("vllm", "all") and VLLM_AVAILABLE:
        all_models.extend(VLLM_MODELS)
    elif model_type == "vllm" and not VLLM_AVAILABLE:
        print("Warning: vLLM requested but not available. Install with: pip install vllm")

    return all_models
