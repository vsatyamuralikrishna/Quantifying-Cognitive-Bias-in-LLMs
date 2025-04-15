import copy

from qcbai.games.prompts.game_rules import PRISONERS_DILEMMA_PERSONALITY_PROMPT
from qcbai.constants.categories import PERSONA_CHOICES

class PersonaPromptGenerator:
    # 1. Refined Descriptive Introduction
    @staticmethod
    def format_persona_intro(self, data):
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
    def format_persona_inline(self, data):
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
    def format_persona_neutral(self, data):
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



    def __init__(self):
        # Create a list of formatting methods
        self.formatting_functions = [
            self.format_persona_intro,
            self.format_persona_inline,
            self.format_persona_neutral
        ]

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
            for format_func in self.formatting_functions:
                formatted_text = format_func(persona_choice)
                # Create a new instance of persona_text for each persona_choice
                persona_text = copy.deepcopy(PRISONERS_DILEMMA_PERSONALITY_PROMPT)
                persona_text[0]["content"] = persona_text[0]["content"].format(PARTNER_PERSONA=formatted_text)
                
                # Create a unique filename based on persona and formatting function
                function_name = format_func.__name__
                yield persona_text, persona_choice, function_name
