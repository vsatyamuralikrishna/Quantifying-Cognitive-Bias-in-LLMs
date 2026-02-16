import re
import uuid
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from qcbai.analytics.types import ExperimentResult, ResponseItem, ModelMetadata
from qcbai.games.game_config import GameConfig


def _normalize_text(text: str) -> str:
    """
    Strip markdown formatting and common LLM output artifacts so that
    the same parser works uniformly across all models.

    Handles variations seen across llama3.2, llama3.3, mistral, mistral-small3.1,
    phi4, gemma3:27b, and qwen2.5:32b:
      - **Bold**, *italic*, __underline__, ~~strikethrough~~
      - "Quoted" or 'Quoted' wrapping
      - Leading bullet markers (-, *, •)
      - Leading labels like "Answer:", "Choice:", "My choice:", "I choose"
      - Leading/trailing whitespace and newlines
    """
    cleaned = text.strip()

    # Remove markdown bold/italic: **word**, *word*, __word__, ~~word~~
    cleaned = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', cleaned)
    cleaned = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', cleaned)
    cleaned = re.sub(r'~~(.*?)~~', r'\1', cleaned)

    # Remove surrounding quotes: "word" or 'word'
    cleaned = re.sub(r'^["\']|["\']$', '', cleaned.strip())

    # Remove leading bullet markers
    cleaned = re.sub(r'^[-*•]\s*', '', cleaned.strip())

    # Remove common preamble patterns (case-insensitive)
    # Matches: "Answer:", "Choice:", "My choice:", "My answer:", "I choose",
    #          "I would choose", "My decision:", "I decide to", "Decision:"
    cleaned = re.sub(
        r'^(?:(?:my\s+)?(?:answer|choice|decision)\s*(?:is)?\s*[:]\s*)',
        '', cleaned.strip(), flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r'^(?:i\s+(?:would\s+)?(?:choose|decide|select|pick)(?:\s+to)?)\s+',
        '', cleaned.strip(), flags=re.IGNORECASE,
    )

    return cleaned.strip()


def parse_binary_response(text: str, game_config: GameConfig) -> Dict:
    """
    Parse LLM output for binary-choice games.

    Unified parser that handles all model output variations:
      - Exact start:       "Silent ..."
      - Markdown bold:     "**Silent** ..."
      - Quoted:            '"Silent" ...'
      - With preamble:     "I choose Silent ..."
      - Anywhere in first sentence: "My decision is to stay Silent."

    Strategy:
      1. Normalize text (strip markdown/quotes/preambles)
      2. Check if normalized text STARTS with either choice (longer first)
      3. If not, search ANYWHERE in the first sentence (longer first)
      4. If still nothing, return Unknown
    """
    choice_a = game_config.trust_choice      # e.g. "Silent", "Swerve", "Contribute"
    choice_b = game_config.distrust_choice   # e.g. "Implicate", "Stay", "Not Contribute"

    # Normalize to handle markdown, quotes, preambles
    cleaned = _normalize_text(text)
    lower = cleaned.lower()

    # Sort choices: check LONGER first to avoid substring conflicts
    # e.g. "Not Contribute" must be checked before "Contribute"
    ordered = sorted(
        [(choice_b, False), (choice_a, True)],
        key=lambda c: len(c[0]),
        reverse=True,
    )

    # --- Pass 1: Check if normalized text STARTS with a choice ---
    for choice, is_trust in ordered:
        if lower.startswith(choice.lower()):
            reason = cleaned[len(choice):].strip().lstrip('.:,;-—').strip()
            return {
                "response": is_trust,
                "decision": choice,
                "amount": None,
                "reason": reason,
            }

    # --- Pass 2: Search ANYWHERE in the first sentence/line ---
    # Take the first line or first sentence (up to period/newline)
    first_chunk = re.split(r'[.\n]', lower, maxsplit=1)[0]
    for choice, is_trust in ordered:
        if choice.lower() in first_chunk:
            # Extract reason: everything after the choice word
            idx = lower.find(choice.lower())
            reason = cleaned[idx + len(choice):].strip().lstrip('.:,;-—').strip()
            return {
                "response": is_trust,
                "decision": choice,
                "amount": None,
                "reason": reason,
            }

    # --- Pass 3: No match found ---
    return {
        "response": None,
        "decision": "Unknown",
        "amount": None,
        "reason": text.strip(),
    }


def parse_amount_response(text: str, game_config: GameConfig) -> Dict:
    """
    Parse LLM output for amount-based games.

    Unified parser that handles all model output variations:
      - Standard:       "$5 because..."
      - Markdown bold:  "**$5** ..."
      - Quoted:         '"$5" ...'
      - With preamble:  "I would give $5..."
      - Bare number:    "5 dollars" or just "5"
      - Decimal:        "$5.00"

    Strategy:
      1. Normalize text (strip markdown/quotes/preambles)
      2. Search for $N pattern ANYWHERE in normalized text
      3. If no $ sign, look for bare number at start or "N dollars"
      4. Clamp to [0, max_amount]
    """
    cleaned = _normalize_text(text)

    # --- Pass 1: Find $N anywhere in the text (most reliable) ---
    match = re.search(r'\$\s*(\d+(?:\.\d+)?)', cleaned)
    if match:
        amount = int(float(match.group(1)))
        amount = max(0, min(amount, game_config.max_amount))
        reason = cleaned[match.end():].strip().lstrip('.:,;-—').strip()
        return {
            "response": True,
            "decision": f"${amount}",
            "amount": amount,
            "reason": reason,
        }

    # --- Pass 2: Bare number at start (e.g. "5", "5 dollars", "5.00") ---
    match = re.match(r'(\d+(?:\.\d+)?)\s*(?:dollars?|USD)?\b', cleaned, re.IGNORECASE)
    if match:
        amount = int(float(match.group(1)))
        amount = max(0, min(amount, game_config.max_amount))
        reason = cleaned[match.end():].strip().lstrip('.:,;-—').strip()
        return {
            "response": True,
            "decision": f"${amount}",
            "amount": amount,
            "reason": reason,
        }

    # --- Pass 3: No parseable amount ---
    return {
        "response": None,
        "decision": "Unknown",
        "amount": None,
        "reason": text.strip(),
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
            timestamp=raw.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
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
        model_slug=model_slug,
        game_type=game_type,
        response_type=game_config.response_type,
        metadata=metadata,
        is_ollama_model=(model_type == "ollama"),
        is_transformer_model=(model_type == "transformers"),
        is_enterprise_model=(model_type == "enterprise"),
    )
