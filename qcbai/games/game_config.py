"""
Game configuration registry.

Each game defines:
  - key: unique identifier used in directories and JSON
  - name: human-readable name
  - response_type: "binary" (two choices) or "amount" (dollar value)
  - choices: the valid response options
  - trust_choice: which choice maps to trust=1 (for binary games)
  - max_amount: upper bound for amount-based games
  - neutral_prompt / personality_prompt: references to prompt templates
  - settings: configurable parameters (used by PGG)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from qcbai.games.prompts.game_rules import (
    PRISONERS_DILEMMA_NEUTRAL_PROMPT,
    PRISONERS_DILEMMA_PERSONALITY_PROMPT,
    DICTATOR_GAME_NEUTRAL_PROMPT,
    DICTATOR_GAME_PERSONALITY_PROMPT,
    CHICKEN_GAME_NEUTRAL_PROMPT,
    CHICKEN_GAME_PERSONALITY_PROMPT,
    ULTIMATUM_GAME_NEUTRAL_PROMPT,
    ULTIMATUM_GAME_PERSONALITY_PROMPT,
    TRUST_GAME_NEUTRAL_PROMPT,
    TRUST_GAME_PERSONALITY_PROMPT,
    PGG_DEFAULT_SETTINGS,
    build_pgg_prompts,
)


@dataclass
class GameConfig:
    key: str
    name: str
    response_type: str  # "binary" or "amount"
    choices: Tuple[str, ...]  # e.g. ("Silent", "Implicate")
    trust_choice: Optional[str]  # for binary: which choice = trust (1)
    distrust_choice: Optional[str]  # for binary: which choice = distrust (0)
    max_amount: Optional[int]  # for amount games
    neutral_prompt: List[Dict[str, str]] = field(default_factory=list)
    personality_prompt: List[Dict[str, str]] = field(default_factory=list)
    settings: Dict = field(default_factory=dict)  # game-specific settings


# ---- Build PGG prompts with default settings ----
_pgg = build_pgg_prompts(PGG_DEFAULT_SETTINGS)


GAME_CONFIGS: Dict[str, GameConfig] = {
    "prisoners_dilemma": GameConfig(
        key="prisoners_dilemma",
        name="Prisoner's Dilemma",
        response_type="binary",
        choices=("Silent", "Implicate"),
        trust_choice="Silent",
        distrust_choice="Implicate",
        max_amount=None,
        neutral_prompt=PRISONERS_DILEMMA_NEUTRAL_PROMPT,
        personality_prompt=PRISONERS_DILEMMA_PERSONALITY_PROMPT,
    ),
    "dictator_game": GameConfig(
        key="dictator_game",
        name="Dictator Game",
        response_type="amount",
        choices=(),
        trust_choice=None,
        distrust_choice=None,
        max_amount=10,
        neutral_prompt=DICTATOR_GAME_NEUTRAL_PROMPT,
        personality_prompt=DICTATOR_GAME_PERSONALITY_PROMPT,
    ),
    "chicken_game": GameConfig(
        key="chicken_game",
        name="Chicken Game",
        response_type="binary",
        choices=("Swerve", "Stay"),
        trust_choice="Swerve",
        distrust_choice="Stay",
        max_amount=None,
        neutral_prompt=CHICKEN_GAME_NEUTRAL_PROMPT,
        personality_prompt=CHICKEN_GAME_PERSONALITY_PROMPT,
    ),
    # PGG Version 1 — Amount: "How much do you contribute?"
    "public_goods_game": GameConfig(
        key="public_goods_game",
        name="Public Goods Game (Amount)",
        response_type="amount",
        choices=(),
        trust_choice=None,
        distrust_choice=None,
        max_amount=PGG_DEFAULT_SETTINGS["ENDOWMENT"],
        neutral_prompt=_pgg["amount_neutral"],
        personality_prompt=_pgg["amount_personality"],
        settings=PGG_DEFAULT_SETTINGS.copy(),
    ),
    # PGG Version 2 — Boolean: "Contribute" or "Not Contribute"
    "public_goods_game_boolean": GameConfig(
        key="public_goods_game_boolean",
        name="Public Goods Game (Boolean)",
        response_type="binary",
        choices=("Contribute", "Not Contribute"),
        trust_choice="Contribute",
        distrust_choice="Not Contribute",
        max_amount=None,
        neutral_prompt=_pgg["boolean_neutral"],
        personality_prompt=_pgg["boolean_personality"],
        settings=PGG_DEFAULT_SETTINGS.copy(),
    ),
    "ultimatum_game": GameConfig(
        key="ultimatum_game",
        name="Ultimatum Game",
        response_type="amount",
        choices=(),
        trust_choice=None,
        distrust_choice=None,
        max_amount=10,
        neutral_prompt=ULTIMATUM_GAME_NEUTRAL_PROMPT,
        personality_prompt=ULTIMATUM_GAME_PERSONALITY_PROMPT,
    ),
    "trust_game": GameConfig(
        key="trust_game",
        name="Trust Game",
        response_type="amount",
        choices=(),
        trust_choice=None,
        distrust_choice=None,
        max_amount=10,
        neutral_prompt=TRUST_GAME_NEUTRAL_PROMPT,
        personality_prompt=TRUST_GAME_PERSONALITY_PROMPT,
    ),
}

ALL_GAME_KEYS = list(GAME_CONFIGS.keys())


def get_game_config(game_key: str) -> GameConfig:
    if game_key not in GAME_CONFIGS:
        raise ValueError(
            f"Unknown game '{game_key}'. Available: {ALL_GAME_KEYS}"
        )
    return GAME_CONFIGS[game_key]


def build_pgg_game_config(settings: dict, version: str = "amount") -> GameConfig:
    """
    Build a custom PGG GameConfig with non-default settings.

    Args:
        settings: dict with keys N, ENDOWMENT, MULTIPLIER, MIN_POSITIVE
        version: "amount" or "boolean"

    Example:
        custom = build_pgg_game_config({"N": 6, "ENDOWMENT": 50, "MULTIPLIER": 2.0, "MIN_POSITIVE": 5})
    """
    merged = {**PGG_DEFAULT_SETTINGS, **settings}
    prompts = build_pgg_prompts(merged)

    if version == "boolean":
        return GameConfig(
            key="public_goods_game_boolean",
            name="Public Goods Game (Boolean)",
            response_type="binary",
            choices=("Contribute", "Not Contribute"),
            trust_choice="Contribute",
            distrust_choice="Not Contribute",
            max_amount=None,
            neutral_prompt=prompts["boolean_neutral"],
            personality_prompt=prompts["boolean_personality"],
            settings=merged,
        )
    else:
        return GameConfig(
            key="public_goods_game",
            name="Public Goods Game (Amount)",
            response_type="amount",
            choices=(),
            trust_choice=None,
            distrust_choice=None,
            max_amount=merged["ENDOWMENT"],
            neutral_prompt=prompts["amount_neutral"],
            personality_prompt=prompts["amount_personality"],
            settings=merged,
        )
