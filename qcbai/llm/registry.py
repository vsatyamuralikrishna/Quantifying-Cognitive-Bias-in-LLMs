from typing import List
from qcbai.llm.base import ModelRunner
from qcbai.llm.ollama import OLLAMA_MODELS
from qcbai.llm.transformers import TRANSFORMER_MODELS

# Future support for:
# from qcbai.llm.openai import OPENAI_MODELS
# from qcbai.llm.gemini import GEMINI_MODELS
# from qcbai.llm.anthropic import ANTHROPIC_MODELS

def get_all_model_runners(model_type: str = "all") -> List[ModelRunner]:
    """
    Returns model runners based on selected type.
    
    Args:
        model_type (str): "ollama", "transformers", "all"
        
    Returns:
        List of ModelRunner instances.
    """
    all_models = []

    if model_type in ("ollama", "all"):
        all_models.extend(OLLAMA_MODELS)

    if model_type in ("transformers", "all"):
        all_models.extend(TRANSFORMER_MODELS)

    # Future support (examples):
    # if model_type in ("openai", "all"):
    #     all_models.extend(OPENAI_MODELS)

    return all_models