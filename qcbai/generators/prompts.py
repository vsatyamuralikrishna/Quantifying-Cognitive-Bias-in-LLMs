import copy
import os
import json
import hashlib
from typing import List, Dict, Generator, Tuple
from qcbai.constants.categories import PERSONA_CHOICES
from qcbai.games.game_config import GameConfig


class PersonaPromptGenerator:
    """
    Generates prompts for any game type by inserting demographic persona
    information into game-specific prompt templates.

    Works with any GameConfig that has neutral_prompt and personality_prompt.
    """

    # --- Formatting styles ---

    @staticmethod
    def format_persona_intro(data):
        if data['gender'] and data['race'] and data['ethnicity']:
            return f"Your partner is a {data['gender']} who identifies as being of {data['race']} race and has an {data['ethnicity']} ethnic background."
        elif data['gender'] and data['race']:
            return f"Your partner is a {data['gender']} who identifies as being of {data['race']} race."
        elif data['gender'] and data['ethnicity']:
            return f"Your partner is a {data['gender']} who has an {data['ethnicity']} ethnic background."
        elif data['race'] and data['ethnicity']:
            return f"Your partner identifies as being of {data['race']} race and has an {data['ethnicity']} ethnic background."
        elif data['gender']:
            return f"Your partner is a {data['gender']}."
        elif data['race']:
            return f"Your partner identifies as being of {data['race']} race."
        elif data['ethnicity']:
            return f"Your partner has an {data['ethnicity']} ethnic background."
        return ""

    @staticmethod
    def format_persona_inline(data):
        if data['gender'] and data['race'] and data['ethnicity']:
            return f"your partner, a {data['gender']} with a {data['race']} racial identity and {data['ethnicity']} ethnic background."
        elif data['gender'] and data['race']:
            return f"your partner, a {data['gender']} with a {data['race']} racial identity."
        elif data['gender'] and data['ethnicity']:
            return f"your partner, a {data['gender']} with an {data['ethnicity']} ethnic background."
        elif data['race'] and data['ethnicity']:
            return f"your partner, with a {data['race']} racial identity and {data['ethnicity']} ethnic background."
        elif data['gender']:
            return f"your partner, a {data['gender']}."
        elif data['race']:
            return f"your partner, who identifies as being of {data['race']} race."
        elif data['ethnicity']:
            return f"your partner, who has an {data['ethnicity']} ethnic background."
        return ""

    @staticmethod
    def format_persona_neutral(data):
        if data['gender'] and data['race'] and data['ethnicity']:
            return f"The partner in question is a {data['gender']} with a {data['race']} racial background and {data['ethnicity']} ethnicity."
        elif data['gender'] and data['race']:
            return f"The partner in question is a {data['gender']} with a {data['race']} racial background."
        elif data['gender'] and data['ethnicity']:
            return f"The partner in question is a {data['gender']} with an {data['ethnicity']} ethnicity."
        elif data['race'] and data['ethnicity']:
            return f"The partner in question is with a {data['race']} racial identity and {data['ethnicity']} ethnicity."
        elif data['gender']:
            return f"The partner in question is a {data['gender']}."
        elif data['race']:
            return f"The partner in question is with a {data['race']} racial identity."
        elif data['ethnicity']:
            return f"The partner in question is with an {data['ethnicity']} ethnicity."
        return ""

    @staticmethod
    def _build_prefix(g: str, r: str, e: str) -> str:
        prefix = ""
        if g and g != "none":
            prefix += "g"
        if r and r != "none":
            prefix += "r"
        if e and e != "none":
            prefix += "e"
        return prefix if prefix else "n"

    def __init__(self):
        self.formatting_functions = {
            "intro": self.format_persona_intro,
            "inline": self.format_persona_inline,
            "neutral": self.format_persona_neutral,
        }

    def generate_persona_prompt(self, game_config: GameConfig):
        """
        Generator that yields formatted persona prompts for every
        persona x style combination, using the given game's personality template.

        Yields:
            (prompt_messages, persona_dict, style_name)
        """
        for persona_choice in PERSONA_CHOICES:
            for style_name, format_func in self.formatting_functions.items():
                formatted_text = format_func(persona_choice)
                prompt = copy.deepcopy(game_config.personality_prompt)
                prompt[0]["content"] = prompt[0]["content"].format(
                    PARTNER_PERSONA=formatted_text
                )
                yield prompt, persona_choice, style_name

    def save_all_persona_prompts(
        self, game_config: GameConfig, output_dir: str
    ) -> int:
        """
        Save all generated persona prompts for a given game into output_dir.

        Returns the count of prompts saved.
        """
        os.makedirs(output_dir, exist_ok=True)
        count = 0

        for prompt, persona_dict, format_name in self.generate_persona_prompt(
            game_config
        ):

            def safe(val):
                return val.replace(" ", "_") if val else "none"

            gender = safe(persona_dict.get("gender"))
            race = safe(persona_dict.get("race"))
            ethnicity = safe(persona_dict.get("ethnicity"))

            filename = (
                f"{format_name}__gender-{gender}__race-{race}__ethnicity-{ethnicity}.json"
            )
            filepath = os.path.join(output_dir, filename)
            prompt_id = os.path.splitext(filename)[0]
            hash_code = hashlib.md5(prompt_id.encode()).hexdigest()[:8]
            prefix = self._build_prefix(gender, race, ethnicity)
            prompt_uid = f"{prefix}-{hash_code}"

            with open(filepath, "w") as f:
                json.dump(
                    {
                        "prompt_id": prompt_id,
                        "prompt_uid": prompt_uid,
                        "game_type": game_config.key,
                        "style": format_name,
                        "persona": persona_dict["persona"],
                        "gender": persona_dict.get("gender"),
                        "race": persona_dict.get("race"),
                        "ethnicity": persona_dict.get("ethnicity"),
                        "prompt": prompt,
                    },
                    f,
                    indent=2,
                )
            count += 1

        print(f"  {count} persona prompts saved to '{output_dir}'")
        return count

    def save_base_prompt(
        self, game_config: GameConfig, output_dir: str
    ) -> None:
        """
        Save a single neutral (no-persona) base prompt for the given game.
        """
        os.makedirs(output_dir, exist_ok=True)

        prompt_id = "base_prompt"
        style = "base"
        base_string = f"{style}__None__None__None"
        hash_code = hashlib.md5(base_string.encode()).hexdigest()[:8]
        prompt_uid = f"b-{hash_code}"

        filename = f"{prompt_id}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(
                {
                    "prompt_id": prompt_id,
                    "prompt_uid": prompt_uid,
                    "game_type": game_config.key,
                    "style": style,
                    "persona": "neutral",
                    "gender": None,
                    "race": None,
                    "ethnicity": None,
                    "prompt": game_config.neutral_prompt,
                },
                f,
                indent=2,
            )

        print(f"  Base prompt saved to '{filepath}'")
