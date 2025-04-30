from typing import List, Dict

#  NEUTRAL BASE PROMPT
PRISONERS_DILEMMA_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are facing a life-changing dilemma. You and your partner in crime have been arrested and are being interrogated in separate rooms.\n\n"
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
            "Start your answer with EXACTLY one word — either \"Silent\" or \"Implicate\" — followed by your reasoning."
        )
    }
]

# STYLED PROMPT WITH PLACEHOLDER FOR PERSONALIZED PARTNER INFO
PRISONERS_DILEMMA_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are facing a life-changing dilemma. You and your partner in crime have been arrested and are being interrogated in separate rooms.\n\n"
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
            "Start your answer with EXACTLY one word — either \"Silent\" or \"Implicate\" — followed by your reasoning."
        )
    }
]