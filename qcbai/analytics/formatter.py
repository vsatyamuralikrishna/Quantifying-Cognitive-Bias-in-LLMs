import re
import uuid
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from qcbai.analytics.types import ExperimentResult, ResponseItem, ModelMetadata
from qcbai.games.game_config import GameConfig


def parse_binary_response(text: str, game_config: GameConfig) -> Dict:
    """
    Parse LLM output for binary-choice games.
    Checks the LONGER choice first to avoid partial-match problems
    (e.g. "Not Contribute" must be checked before "Contribute").
    """
    text = text.strip()
    choice_a = game_config.trust_choice      # e.g. "Silent", "Swerve", "Contribute"
    choice_b = game_config.distrust_choice   # e.g. "Implicate", "Stay", "Not Contribute"

    lower = text.lower()

    # Check longer choice first to avoid substring conflicts
    ordered = sorted(
        [(choice_b, False), (choice_a, True)],
        key=lambda c: len(c[0]),
        reverse=True,
    )

    for choice, is_trust in ordered:
        if lower.startswith(choice.lower()):
            return {
                "response": is_trust,
                "decision": choice,
                "amount": None,
                "reason": text[len(choice):].strip(),
            }

    return {
        "response": None,
        "decision": "Unknown",
        "amount": None,
        "reason": text,
    }


def parse_amount_response(text: str, game_config: GameConfig) -> Dict:
    """
    Parse LLM output for amount-based games (Dictator, Public Goods, Ultimatum, Trust).
    Expects the response to start with a dollar amount like $5.
    """
    text = text.strip()
    match = re.match(r"\$\s*(\d+)", text)
    if match:
        amount = int(match.group(1))
        amount = max(0, min(amount, game_config.max_amount))
        reason = text[match.end():].strip()
        return {
            "response": True,
            "decision": f"${amount}",
            "amount": amount,
            "reason": reason,
        }
    else:
        return {
            "response": None,
            "decision": "Unknown",
            "amount": None,
            "reason": text,
        }


def parse_response_text(text: str, game_config: GameConfig) -> Dict:
    """
    Route to the correct parser based on game response type.
    """
    if game_config.response_type == "binary":
        return parse_binary_response(text, game_config)
    else:
        return parse_amount_response(text, game_config)


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
    game_config: GameConfig,
    temperature: float = 0.7,
    additional_config: Optional[Dict] = None,
) -> ExperimentResult:
    """
    Create a full experiment result with metrics appropriate to the game type.
    """
    parsed_items = []
    binary_list = []
    amount_list = []

    for idx, raw in enumerate(prompt_responses):
        text = raw.get("response_text", "")
        parsed = parse_response_text(text, game_config)

        parsed_items.append(ResponseItem(
            id=raw["id"],
            response_text=text,
            decision=parsed["decision"],
            reason=parsed["reason"],
            response=parsed["response"] if parsed["response"] is not None else False,
            amount=parsed.get("amount"),
            iteration=idx + 1,
            response_time=raw.get("response_time", 0.0),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))

        if game_config.response_type == "binary":
            if parsed["response"] is True:
                binary_list.append(1)
            else:
                binary_list.append(0)
        else:
            amount_list.append(parsed.get("amount"))

    # Compute metrics
    if game_config.response_type == "binary":
        total = len(binary_list)
        trust = sum(binary_list)
        trust_estimate = round(trust / total, 3) if total else 0.0
        distrust_estimate = round(1 - trust_estimate, 3)
        result_list = binary_list
        amounts = None
        mean_amount = None
    else:
        valid_amounts = [a for a in amount_list if a is not None]
        total = len(valid_amounts)
        mean_amount = round(sum(valid_amounts) / total, 2) if total else 0.0
        trust_estimate = round(mean_amount / game_config.max_amount, 3) if game_config.max_amount else 0.0
        distrust_estimate = round(1 - trust_estimate, 3)
        result_list = [a if a is not None else 0 for a in amount_list]
        amounts = valid_amounts

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
        result=result_list,
        trust_estimate_probability_distribution=trust_estimate,
        distrust_estimate_probability_distribution=distrust_estimate,
        mean_amount=mean_amount,
        total_runs=total,
        model_name=model_name,
        game_type=game_type,
        response_type=game_config.response_type,
        metadata=metadata,
        is_ollama_model=(model_type == "ollama"),
        is_transformer_model=(model_type == "transformers"),
        is_enterprise_model=(model_type == "enterprise"),
    )
