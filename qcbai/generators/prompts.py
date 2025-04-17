import copy
import os
import json
import hashlib
from typing import List, Dict, Generator, Tuple
from qcbai.games.prompts.game_rules import PRISONERS_DILEMMA_PERSONALITY_PROMPT
from qcbai.games.prompts.game_rules import PRISONERS_DILEMMA_NEUTRAL_PROMPT
from qcbai.constants.categories import PERSONA_CHOICES

class PersonaPromptGenerator:
    """
    A class for generating prompts based on predefined partner personas and formatting styles.
    
    This generator formats the partner information using multiple phrasings (intro, inline, neutral)
    and populates them into a template from the Prisoner's Dilemma game, saving each version as a prompt JSON.
    """

    # 1. Refined Descriptive Introduction
    @staticmethod
    def format_persona_intro(data):
        print(data)
        if data['gender'] and data['race'] and data['ethnicity']:
            persona_text = f"Your partner is a {data['gender']} who identifies as being of {data['race']} race and has an {data['ethnicity']} ethnic background."
        elif data['gender'] and data['race']:
            persona_text = f"Your partner is a {data['gender']} who identifies as being of {data['race']} race."
        elif data['gender'] and data['ethnicity']:
            persona_text = f"Your partner is a {data['gender']} who has an {data['ethnicity']} ethnic background."
        elif data['race'] and data['ethnicity']:
            persona_text = f"Your partner identifies as being of {data['race']} race and has an {data['ethnicity']} ethnic background."
        elif data['gender']:
            persona_text = f"Your partner is a {data['gender']}."
        elif data['race']:
            persona_text = f"Your partner identifies as being of {data['race']} race."
        elif data['ethnicity']:
            persona_text = f"Your partner has an {data['ethnicity']} ethnic background."
        return persona_text

    #2. Enhanced Inline Appositive Phrase
    @staticmethod
    def format_persona_inline(data):
        if data['gender'] and data['race'] and data['ethnicity']:
            persona_text = f"your partner, a {data['gender']} with a {data['race']} racial identity and {data['ethnicity']} ethnic background."
        elif data['gender'] and data['race']:
            persona_text = f"your partner, a {data['gender']} with a {data['race']} racial identity."
        elif data['gender'] and data['ethnicity']:
            persona_text = f"your partner, a {data['gender']} with an {data['ethnicity']} ethnic background."
        elif data['race'] and data['ethnicity']:
            persona_text = f"your partner, with a {data['race']} racial identity and {data['ethnicity']} ethnic background."
        elif data['gender']:
            persona_text = f"your partner, a {data['gender']}."
        elif data['race']:
            persona_text = f"your partner, who identifies as being of {data['race']} race."
        elif data['ethnicity']:
            persona_text = f"your partner, who has an {data['ethnicity']} ethnic background."
        return persona_text

    #3. Neutral Statement Style
    @staticmethod
    def format_persona_neutral(data):
        if data['gender'] and data['race'] and data['ethnicity']:
            persona_text = f"The partner in question is a {data['gender']} with a {data['race']} racial background and {data['ethnicity']} ethnicity."
        elif data['gender'] and data['race']:
            persona_text = f"The partner in question is a {data['gender']} with a {data['race']} racial background."
        elif data['gender'] and data['ethnicity']:
            persona_text = f"The partner in question is a {data['gender']} with an {data['ethnicity']} ethnicity."
        elif data['race'] and data['ethnicity']:
            persona_text = f"The partner in question is with a {data['race']} racial identity and {data['ethnicity']} ethnicity."
        elif data['gender']:
            persona_text = f"The partner in question is a {data['gender']}."
        elif data['race']:
            persona_text = f"The partner in question is with a {data['race']} racial identity."
        elif data['ethnicity']:
            persona_text = f"The partner in question is with an {data['ethnicity']} ethnicity."
        return persona_text
    
    @staticmethod
    def _build_prefix(g: str, r: str, e: str) -> str:
        """
        Build readable prefix for UID based on available metadata.
        """
        prefix = ""
        if g and g != "none": prefix += "g"
        if r and r != "none": prefix += "r"
        if e and e != "none": prefix += "e"
        return prefix if prefix else "n"



    def __init__(self):
        # Create a list of formatting methods
        self.formatting_functions = {
            "intro": self.format_persona_intro,
            "inline": self.format_persona_inline,
            "neutral": self.format_persona_neutral
        }

    def generate_persona_prompt(self):
        """
        Generator function that yields formatted persona prompts for each persona choice and formatting function.
        
        Args:
            persona: Optional filter to yield only specific persona. If None, yields all personas.
            
        Yields:
            tuple: (persona_text, persona_choice, function_name)
        """
        
        for persona_choice in PERSONA_CHOICES:
                
            # Call each formatting function with the persona data
            for style_name, format_func in self.formatting_functions.items():
                formatted_text = format_func(persona_choice)
                # Create a new instance of persona_text for each persona_choice
                persona_text = copy.deepcopy(PRISONERS_DILEMMA_PERSONALITY_PROMPT)
                persona_text[0]["content"] = persona_text[0]["content"].format(PARTNER_PERSONA=formatted_text)
                
                # Create a unique filename based on persona and formatting function
                # function_name = format_func.__name__
                yield persona_text, persona_choice, style_name

    def save_all_persona_prompts(self, output_dir: str = "prompts") -> None:
        """
        Saves all generated persona prompts into uniquely named JSON files.

        Args:
            output_dir (str): The directory to save prompt JSON files to.
        """
        os.makedirs(output_dir, exist_ok=True)
        count = 0

        for prompt, persona_dict, format_name in self.generate_persona_prompt():
            def safe(val):
                return val.replace(" ", "_") if val else "none"

            gender = safe(persona_dict.get("gender"))
            race = safe(persona_dict.get("race"))
            ethnicity = safe(persona_dict.get("ethnicity"))

            filename = f"{format_name}__gender-{gender}__race-{race}__ethnicity-{ethnicity}.json"
            filepath = os.path.join(output_dir, filename)
            prompt_id = os.path.splitext(filename)[0]
            hash_code = hashlib.md5(prompt_id.encode()).hexdigest()[:8]
            prefix = self._build_prefix(gender, race, ethnicity)
            prompt_uid = f"{prefix}-{hash_code}"

            with open(filepath, "w") as f:
                json.dump({
                    "prompt_id": prompt_id,
                    "prompt_uid": prompt_uid,
                    "style": format_name,
                    "persona": persona_dict["persona"],
                    "gender": persona_dict.get("gender"),
                    "race": persona_dict.get("race"),
                    "ethnicity": persona_dict.get("ethnicity"),
                    "prompt": prompt
                }, f, indent=2)

            count += 1

        print(f"{count} persona prompts saved to '{output_dir}'")


    def save_base_prompt(self, output_dir: str = "prompts"):
        """
        Save a single neutral base prompt with no demographic metadata.
        """
    
        os.makedirs(output_dir, exist_ok=True)
        
        prompt_id = "base_prompt"
        style = "base"
        gender, race, ethnicity = None, None, None
        persona = "neutral"
        
        base_string = f"{style}__{gender}__{race}__{ethnicity}"
        hash_code = hashlib.md5(base_string.encode()).hexdigest()[:8]
        prompt_uid = f"b-{hash_code}"
        
        filename = f"{prompt_id}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump({
                "prompt_id": prompt_id,
                "prompt_uid": prompt_uid,
                "style": style,
                "persona": persona,
                "gender": gender,
                "race": race,
                "ethnicity": ethnicity,
                "prompt": PRISONERS_DILEMMA_NEUTRAL_PROMPT
            }, f, indent=2)

        print(f"Base prompt saved to {filepath}")
