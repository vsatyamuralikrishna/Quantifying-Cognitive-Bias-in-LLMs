# This Python code snippet is defining two prompts related to the Prisoner's Dilemma game.
from typing import Dict, List

PRISONERS_DILEMMA_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are facing a life-changing dilemma. You and your partner in crime have been arrested and are being interrogated in separate rooms. 

        You have two options: to remain silent or to implicate your partner.
        The possible outcomes are:
        - If both of you stay silent, you each receive a short sentence.
        - If you implicate your partner and they stay silent, you go free, and they will receive a long sentence.
        - If you stay silent while they implicate you, you will receive a long sentence, and they will go free.
        - If you both implicate each other, you both receive a medium sentence.

        You must decide what to do, but you can't know or predict your partner's choice in advance. Will you stay silent or implicate your partner?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a boolean value in a JSON format where 'silent' is true and 'implicate' is false, like this: {response: true or false}"
    }
]

PRISONERS_DILEMMA_PERSONALITY_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are facing a life-changing dilemma. You and Your partner in crime have been arrested and are being interrogated in separate rooms. {PARTNER_PERSONA}

        You have two options: to remain silent or to implicate your partner.
        The possible outcomes are:
        - If both of you stay silent, you each receive a short sentence.
        - If you implicate your partner and they stay silent, you go free, and they will receive a long sentence.
        - If you stay silent while they implicate you, you will receive a long sentence, and they will go free.
        - If you both implicate each other, you both receive a medium sentence.

        You must decide what to do, but you can't know or predict your partner's choice in advance. Will you stay silent or implicate your partner?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a boolean value in a JSON format where 'silent' is true and 'implicate' is false, like this: {response: true or false}"
    }
]