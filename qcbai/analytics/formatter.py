import uuid
import hashlib
from typing import List, Dict, Optional
from qcbai.analytics.types import ExperimentResult, ResponseItem, ModelMetadata


def compute_uid(prompt_id: str, model_slug: str) -> str:
    """
    Generate a reproducible hash-based prompt_uid from prompt_id and model_slug.
    """
    hash_code = hashlib.md5(f"{prompt_id}_{model_slug}".encode()).hexdigest()[:8]
    return f"{model_slug}-{hash_code}"


def parse_response_text(text: str) -> Optional[bool]:
    """
    Try to convert the LLM response text into a boolean value.
    Assumes either { "response": true/false } or matching keywords.
    """
    try:
        if "false" in text.lower():
            return False
        elif "true" in text.lower():
            return True
    except Exception:
        pass
    return None


def create_result_entry(
    *,
    model_slug: str,
    model_name: str,
    model_type: str,  # "ollama" | "transformers" | "enterprise"
    prompt_id: str,
    persona_dict: Dict,
    prompt_style: str,
    prompt_responses: List[str],
    execution_id: Optional[str],
    game_type: str,
    temperature: float = 0.7,
    additional_config: Optional[Dict] = None,
) -> ExperimentResult:
    """
    Build and return an ExperimentResult object from all prompt responses.
    """
    # Convert raw LLM responses to response objects
    parsed_items = []
    binary_list = []

    for raw_text in prompt_responses:
        val = parse_response_text(raw_text)
        parsed_items.append(ResponseItem(
            id=str(uuid.uuid4()),
            response_text=raw_text,
            response=val if val is not None else False
        ))
        binary_list.append(1 if val is True else 0)

    total = len(binary_list)
    trust = sum(binary_list)
    distrust = total - trust

    trust_estimate = round(trust / total, 3) if total else 0.0
    distrust_estimate = round(distrust / total, 3) if total else 0.0

    # Determine metadata flags
    is_ollama = model_type == "ollama"
    is_transformer = model_type == "transformers"
    is_enterprise = model_type == "enterprise"

    # 🌱 Metadata per model type
    metadata = ModelMetadata(
        name=model_name,
        ollama_config=additional_config if is_ollama else None,
        transformer_model_config=additional_config if is_transformer else None,
        enterprise_model_config=additional_config if is_enterprise else None,
    )

    return ExperimentResult(
        gender=persona_dict.get("gender"),
        race=persona_dict.get("race"),
        ethnicity=persona_dict.get("ethnicity"),
        persona=persona_dict.get("persona"),
        style=prompt_style,
        prompt_name=prompt_id,
        prompt_id=prompt_id,
        persona_uid=persona_dict.get("persona_uid", "unknown"),
        execution_id=execution_id or str(uuid.uuid4()),
        prompt_responses={"responses": parsed_items},
        result=binary_list,
        trust_estimate_probability_distribution=trust_estimate,
        distrust_estimate_probability_distribution=distrust_estimate,
        total_runs=total,
        model_name=model_slug,
        game_type=game_type,
        metadata=metadata,
        is_ollama_model=is_ollama,
        is_transformer_model=is_transformer,
        is_enterprise_model=is_enterprise
    )