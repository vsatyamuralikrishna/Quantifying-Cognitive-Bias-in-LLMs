import uuid
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from qcbai.analytics.types import ExperimentResult, ResponseItem, ModelMetadata


def parse_response_text(text: str) -> Dict:
    """
    Parse the LLM output to extract decision and reasoning.
    Expects format starting with "Silent" or "Implicate".
    """
    text = text.strip()
    decision = ""
    reason = ""
    response_bool = False

    if text.lower().startswith("silent"):
        decision = "Silent"
        reason = text[6:].strip()
        response_bool = True
    elif text.lower().startswith("implicate"):
        decision = "Implicate"
        reason = text[9:].strip()
        response_bool = False
    else:
        decision = "Unknown"
        reason = text

    return {
        "response": response_bool,
        "decision": decision,
        "reason": reason
    }


def compute_uid(prompt_id: str, model_slug: str) -> str:
    hash_code = hashlib.md5(f"{prompt_id}_{model_slug}".encode()).hexdigest()[:8]
    return f"{model_slug}-{hash_code}"


def create_result_entry(
    *,
    model_slug: str,
    model_name: str,
    model_type: str,
    prompt_id: str,
    persona_dict: Dict,
    prompt_style: str,
    prompt_responses: List[Dict],
    execution_id: Optional[str],
    game_type: str,
    temperature: float = 0.7,
    additional_config: Optional[Dict] = None,
) -> ExperimentResult:
    """
    Create a full experiment result object with trust metrics and structured metadata.
    """
    parsed_items = []
    binary_list = []

    for idx, raw in enumerate(prompt_responses):
        text = raw.get("response_text", "")
        start = time.time()
        parsed = parse_response_text(text)
        end = time.time()

        parsed_items.append(ResponseItem(
            id=raw["id"],
            response_text=text,
            decision=parsed["decision"],
            reason=parsed["reason"],
            response=parsed["response"],
            iteration=idx + 1,
            response_time=round(end - start, 4),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        binary_list.append(1 if parsed["response"] else 0)

    trust = sum(binary_list)
    total = len(binary_list)
    distrust = total - trust

    trust_estimate = round(trust / total, 3) if total else 0.0
    distrust_estimate = round(distrust / total, 3) if total else 0.0

    now = datetime.now()

    metadata = ModelMetadata(
        name=model_name,
        ollama_config=additional_config if model_type == "ollama" else None,
        transformer_model_config=additional_config if model_type == "transformers" else None,
        enterprise_model_config=additional_config if model_type == "enterprise" else None,
    )

    return ExperimentResult(
        gender=persona_dict.get("gender"),
        race=persona_dict.get("race"),
        ethnicity=persona_dict.get("ethnicity"),
        persona=persona_dict.get("persona"),
        style=prompt_style,
        prompt_name=prompt_id,
        prompt_id=prompt_id,
        persona_uid=persona_dict.get("persona_uid", ""),
        execution_id=execution_id or str(uuid.uuid4()),
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S"),
        timestamp=now.isoformat(),
        prompt_responses={"responses": parsed_items},
        result=binary_list,
        trust_estimate_probability_distribution=trust_estimate,
        distrust_estimate_probability_distribution=distrust_estimate,
        total_runs=total,
        model_name=model_name,
        game_type=game_type,
        metadata=metadata,
        is_ollama_model=(model_type == "ollama"),
        is_transformer_model=(model_type == "transformers"),
        is_enterprise_model=(model_type == "enterprise")
    )