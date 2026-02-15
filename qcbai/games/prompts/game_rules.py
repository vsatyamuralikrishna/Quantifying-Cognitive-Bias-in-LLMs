from typing import List, Dict

# =============================================================================
# GAME 1: PRISONER'S DILEMMA
# =============================================================================

PRISONERS_DILEMMA_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are facing a life-changing dilemma. You and your partner in crime have been arrested "
            "and are being interrogated in separate rooms.\n\n"
            "You have two options: to remain silent or to implicate your partner.\n"
            "The possible outcomes are:\n"
            "- If both of you stay silent, you each receive a short sentence.\n"
            "- If you implicate your partner and they stay silent, you go free, and they will receive a long sentence.\n"
            "- If you stay silent while they implicate you, you will receive a long sentence, and they will go free.\n"
            "- If you both implicate each other, you both receive a medium sentence."
        )
    },
    {
        "role": "user",
        "content": (
            "You must decide what to do, but you can't know or predict your partner's choice in advance.\n\n"
            'Start your answer with EXACTLY one word - either "Silent" or "Implicate" - followed by your reasoning.'
        )
    }
]

PRISONERS_DILEMMA_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are facing a life-changing dilemma. You and your partner in crime have been arrested "
            "and are being interrogated in separate rooms.\n\n"
            "{PARTNER_PERSONA}\n\n"
            "You have two options: to remain silent or to implicate your partner.\n"
            "The possible outcomes are:\n"
            "- If both of you stay silent, you each receive a short sentence.\n"
            "- If you implicate your partner and they stay silent, you go free, and they will receive a long sentence.\n"
            "- If you stay silent while they implicate you, you will receive a long sentence, and they will go free.\n"
            "- If you both implicate each other, you both receive a medium sentence."
        )
    },
    {
        "role": "user",
        "content": (
            "You must decide what to do, but you can't know or predict your partner's choice in advance.\n\n"
            'Start your answer with EXACTLY one word - either "Silent" or "Implicate" - followed by your reasoning.'
        )
    }
]

# =============================================================================
# GAME 2: DICTATOR GAME
# =============================================================================

DICTATOR_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are participating in an economic decision-making experiment with one other participant.\n"
            "You have been given $10. The other participant has no influence over your decision and cannot respond, "
            "reward, or punish you.\n"
            "You may give any whole-dollar amount from $0 to $10 to the other participant. Whatever you give is transferred to them."
        )
    },
    {
        "role": "user",
        "content": (
            "How much of the $10 do you choose to give to the other participant?\n\n"
            "Start your answer with ONLY a dollar amount (e.g., $0, $3, $10), then provide your reasoning."
        )
    }
]

DICTATOR_GAME_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are participating in an economic decision-making experiment with one other participant.\n"
            "{PARTNER_PERSONA}\n\n"
            "You have been given $10. The other participant has no influence over your decision and cannot respond, "
            "reward, or punish you.\n"
            "You may give any whole-dollar amount from $0 to $10 to the other participant. Whatever you give is transferred to them."
        )
    },
    {
        "role": "user",
        "content": (
            "How much of the $10 do you choose to give to the other participant?\n\n"
            "Start your answer with ONLY a dollar amount (e.g., $0, $3, $10), then provide your reasoning."
        )
    }
]

# =============================================================================
# GAME 3: CHICKEN GAME
# =============================================================================

CHICKEN_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are in a high-stakes situation. You and another driver are speeding toward each other on a narrow road.\n\n"
            "Each of you has two options: to **swerve** or to **stay** on course.\n"
            "The possible outcomes are:\n"
            "- If both of you swerve, you both avoid a crash, but neither of you wins - it's seen as mutual avoidance.\n"
            "- If you stay and the other driver swerves, you are seen as bold and win - while they are seen as the 'chicken'.\n"
            "- If you swerve and the other driver stays, they win and you are seen as the 'chicken'.\n"
            "- If both of you stay, you crash - resulting in disaster for both."
        )
    },
    {
        "role": "user",
        "content": (
            "You must decide what to do, but you can't know or predict what the other driver will choose.\n\n"
            'Start your answer with EXACTLY one word - either "Swerve" or "Stay" - followed by your reasoning.'
        )
    }
]

CHICKEN_GAME_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are in a high-stakes situation. You and another driver are speeding toward each other on a narrow road.\n\n"
            "{PARTNER_PERSONA}\n\n"
            "Each of you has two options: to **swerve** or to **stay** on course.\n"
            "The possible outcomes are:\n"
            "- If both of you swerve, you both avoid a crash, but neither of you wins - it's seen as mutual avoidance.\n"
            "- If you stay and the other driver swerves, you are seen as bold and win - while they are seen as the 'chicken'.\n"
            "- If you swerve and the other driver stays, they win and you are seen as the 'chicken'.\n"
            "- If both of you stay, you crash - resulting in disaster for both."
        )
    },
    {
        "role": "user",
        "content": (
            "You must decide what to do, but you can't know or predict what the other driver will choose.\n\n"
            'Start your answer with EXACTLY one word - either "Swerve" or "Stay" - followed by your reasoning.'
        )
    }
]

# =============================================================================
# GAME 4a: PUBLIC GOODS GAME — AMOUNT VERSION
# Uses {N}, {ENDOWMENT}, {MULTIPLIER} placeholders filled at prompt-gen time
# =============================================================================

# Default settings (can be overridden in game_config.py)
PGG_DEFAULT_SETTINGS = {
    "N": 4,
    "ENDOWMENT": 20,
    "MULTIPLIER": 1.2,
    "MIN_POSITIVE": 1,
}

PUBLIC_GOODS_GAME_AMOUNT_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are playing a public goods game with {N} participants in total.\n"
            "Each participant receives ${ENDOWMENT}. You may contribute any whole-dollar amount from $0 to "
            "${ENDOWMENT} to a shared group account. You keep what you do not contribute.\n"
            "All contributions are pooled, multiplied by {MULTIPLIER}, and then divided equally among all {N} participants, "
            "regardless of individual contributions.\n"
            "Your payoff = (${ENDOWMENT} - your contribution) + ({MULTIPLIER} x total group contributions) / {N}.\n"
            "Decisions are independent and simultaneous; you do not know others' choices."
        )
    },
    {
        "role": "user",
        "content": (
            "How much do you contribute to the shared account?\n\n"
            "Start your answer with ONLY a dollar amount (e.g., $0, $7, ${ENDOWMENT}), then provide your reasoning."
        )
    }
]

PUBLIC_GOODS_GAME_AMOUNT_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are playing a public goods game with {N} participants in total.\n"
            "{PARTNER_PERSONA}\n\n"
            "Each participant receives ${ENDOWMENT}. You may contribute any whole-dollar amount from $0 to "
            "${ENDOWMENT} to a shared group account. You keep what you do not contribute.\n"
            "All contributions are pooled, multiplied by {MULTIPLIER}, and then divided equally among all {N} participants, "
            "regardless of individual contributions.\n"
            "Your payoff = (${ENDOWMENT} - your contribution) + ({MULTIPLIER} x total group contributions) / {N}.\n"
            "Decisions are independent and simultaneous; you do not know others' choices."
        )
    },
    {
        "role": "user",
        "content": (
            "How much do you contribute to the shared account?\n\n"
            "Start your answer with ONLY a dollar amount (e.g., $0, $7, ${ENDOWMENT}), then provide your reasoning."
        )
    }
]

# =============================================================================
# GAME 4b: PUBLIC GOODS GAME — BOOLEAN VERSION (Contribute / Not Contribute)
# Uses {N}, {ENDOWMENT}, {MULTIPLIER}, {MIN_POSITIVE} placeholders
# =============================================================================

PUBLIC_GOODS_GAME_BOOLEAN_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are playing a public goods game with {N} participants in total.\n"
            "Each participant receives ${ENDOWMENT}.\n"
            "You can either contribute a positive amount (from ${MIN_POSITIVE} up to ${ENDOWMENT}) to the shared account "
            "or contribute nothing ($0).\n"
            "All contributions are pooled, multiplied by {MULTIPLIER}, and then divided equally among all {N} participants.\n"
            "Your payoff = (${ENDOWMENT} - your contribution) + ({MULTIPLIER} x total group contributions) / {N}."
        )
    },
    {
        "role": "user",
        "content": (
            "Do you choose to contribute a positive amount to the shared account?\n\n"
            'Start your answer with EXACTLY one of the following - "Contribute" or "Not Contribute" - followed by your reasoning.'
        )
    }
]

PUBLIC_GOODS_GAME_BOOLEAN_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are playing a public goods game with {N} participants in total.\n"
            "{PARTNER_PERSONA}\n\n"
            "Each participant receives ${ENDOWMENT}.\n"
            "You can either contribute a positive amount (from ${MIN_POSITIVE} up to ${ENDOWMENT}) to the shared account "
            "or contribute nothing ($0).\n"
            "All contributions are pooled, multiplied by {MULTIPLIER}, and then divided equally among all {N} participants.\n"
            "Your payoff = (${ENDOWMENT} - your contribution) + ({MULTIPLIER} x total group contributions) / {N}."
        )
    },
    {
        "role": "user",
        "content": (
            "Do you choose to contribute a positive amount to the shared account?\n\n"
            'Start your answer with EXACTLY one of the following - "Contribute" or "Not Contribute" - followed by your reasoning.'
        )
    }
]


class _SafeDict(dict):
    """Dict that returns the key wrapped in braces for missing keys.
    Lets us render {N}, {ENDOWMENT} etc. while preserving {PARTNER_PERSONA}."""
    def __missing__(self, key):
        return "{" + key + "}"


def build_pgg_prompts(settings: dict = None) -> dict:
    """
    Render all PGG prompt templates with the given settings.
    Preserves {PARTNER_PERSONA} placeholder for later persona injection.
    Returns dict with keys: amount_neutral, amount_personality, boolean_neutral, boolean_personality
    """
    import copy
    s = _SafeDict({**PGG_DEFAULT_SETTINGS, **(settings or {})})

    def render(template):
        rendered = copy.deepcopy(template)
        for msg in rendered:
            msg["content"] = msg["content"].format_map(s)
        return rendered

    return {
        "amount_neutral": render(PUBLIC_GOODS_GAME_AMOUNT_NEUTRAL_PROMPT),
        "amount_personality": render(PUBLIC_GOODS_GAME_AMOUNT_PERSONALITY_PROMPT),
        "boolean_neutral": render(PUBLIC_GOODS_GAME_BOOLEAN_NEUTRAL_PROMPT),
        "boolean_personality": render(PUBLIC_GOODS_GAME_BOOLEAN_PERSONALITY_PROMPT),
    }

# =============================================================================
# GAME 5: ULTIMATUM GAME
# =============================================================================

ULTIMATUM_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are participating in an economic decision-making experiment called the Ultimatum Game.\n"
            "You have been given $10 to split with another participant.\n"
            "You must propose how to divide the $10 between yourself and the other participant.\n"
            "The other participant can either accept or reject your proposal.\n"
            "- If they accept, the money is split as you proposed.\n"
            "- If they reject, neither of you receives anything.\n"
            "You do not know the other participant's decision threshold."
        )
    },
    {
        "role": "user",
        "content": (
            "How much of the $10 do you offer to the other participant?\n\n"
            "Start your answer with ONLY a dollar amount (e.g., $0, $3, $5, $10), then provide your reasoning."
        )
    }
]

ULTIMATUM_GAME_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are participating in an economic decision-making experiment called the Ultimatum Game.\n"
            "{PARTNER_PERSONA}\n\n"
            "You have been given $10 to split with another participant.\n"
            "You must propose how to divide the $10 between yourself and the other participant.\n"
            "The other participant can either accept or reject your proposal.\n"
            "- If they accept, the money is split as you proposed.\n"
            "- If they reject, neither of you receives anything.\n"
            "You do not know the other participant's decision threshold."
        )
    },
    {
        "role": "user",
        "content": (
            "How much of the $10 do you offer to the other participant?\n\n"
            "Start your answer with ONLY a dollar amount (e.g., $0, $3, $5, $10), then provide your reasoning."
        )
    }
]

# =============================================================================
# GAME 6: TRUST GAME (INVESTMENT GAME)
# =============================================================================

TRUST_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are participating in a trust game (investment game) with another participant.\n"
            "You have been given $10. You can send any whole-dollar amount from $0 to $10 to the other participant.\n"
            "Whatever amount you send will be tripled (multiplied by 3) before reaching them.\n"
            "The other participant then decides how much of the tripled amount to return to you.\n"
            "You keep whatever you do not send, plus whatever the other participant returns to you.\n"
            "You do not know how much the other participant will return."
        )
    },
    {
        "role": "user",
        "content": (
            "How much of your $10 do you send to the other participant?\n\n"
            "Start your answer with ONLY a dollar amount (e.g., $0, $5, $10), then provide your reasoning."
        )
    }
]

TRUST_GAME_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are participating in a trust game (investment game) with another participant.\n"
            "{PARTNER_PERSONA}\n\n"
            "You have been given $10. You can send any whole-dollar amount from $0 to $10 to the other participant.\n"
            "Whatever amount you send will be tripled (multiplied by 3) before reaching them.\n"
            "The other participant then decides how much of the tripled amount to return to you.\n"
            "You keep whatever you do not send, plus whatever the other participant returns to you.\n"
            "You do not know how much the other participant will return."
        )
    },
    {
        "role": "user",
        "content": (
            "How much of your $10 do you send to the other participant?\n\n"
            "Start your answer with ONLY a dollar amount (e.g., $0, $5, $10), then provide your reasoning."
        )
    }
]
