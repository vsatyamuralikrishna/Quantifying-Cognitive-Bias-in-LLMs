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

INVESTOR_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are participating in a two-player trust game. You are Player A (the investor), and your partner is Player B (the trustee).

        You must decide whether to invest your money with Player B or keep it.

        If you choose to invest:
        - The amount will be tripled and given to Player B.
        - Player B will then decide how much to return to you — possibly nothing, or something in return.

        If you choose not to invest:
        - You keep the money, and the game ends.

        You cannot communicate with or predict Player B’s actions.

        Will you invest the money with Player B?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will invest, or {\"response\": false} if not."
    }
]

HIRING_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are a hiring manager evaluating a candidate for a critical job position. You have reviewed their qualifications and conducted an interview. Now, you must decide whether to trust the candidate enough to offer them the job.

        If you hire them:
        - They may thrive and become a valuable team member — or they may reject the offer or underperform, costing time and resources.

        If you don’t hire them:
        - You avoid risk, but may miss out on a potentially great hire.

        Will you trust the candidate and offer them the job?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will offer the job, or {\"response\": false} if not."
    }
]

ENVELOPE_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are playing a two-player trust game. You are Player B.

        Player A has placed a sum of money inside a sealed envelope and handed it to you. They claim that the envelope contains the full amount they promised.

        However, you have no way of verifying the contents without opening the envelope. If you choose to open it, the trust is broken, and you forfeit the money regardless of the amount inside.

        If you choose to accept the envelope without opening it, you keep whatever amount is inside — for better or worse.

        You must now decide whether to **trust** Player A and accept the envelope without checking, or to **distrust** and open it, forfeiting the reward.

        Will you trust Player A and accept the envelope without opening it?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will trust and accept the envelope, or {\"response\": false} if you will open it and forfeit the reward."
    }
]
CONTRACTOR_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are working with a contractor (Player B) who has agreed to complete a task for you — such as developing a project, designing a product, or providing a service.

        You must now decide whether to **pay the full amount upfront** or to pay only after the work is completed.

        If you pay upfront:
        - Player B might do the work as promised and deliver great results — or they might disappear without delivering anything.

        If you wait to pay:
        - Player B might refuse to start the work without an upfront payment.

        You cannot negotiate or communicate further. Will you trust the contractor and pay upfront?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will pay upfront, or {\"response\": false} if you will wait until after delivery."
    }
]
HOUSE_SITTING_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are leaving town for several days and need someone to watch your house while you're away. Player B has offered to house-sit for you.

        You don’t know Player B very well, but they seem trustworthy. You have no way to monitor what they do while you're gone.

        If you let them house-sit:
        - They may take good care of your property — or they may damage or misuse it.

        If you don’t trust them:
        - You’ll need to make other arrangements or leave your house unattended.

        Will you trust Player B and give them the keys to your house?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will trust them with the keys, or {\"response\": false} if not."
    }
]
COLLABORATOR_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are part of a two-person team working on a collaborative project. You have spent considerable time preparing valuable notes and ideas that could help complete the work faster and better.

        You must now decide whether to share your notes with your teammate (Player B).

        If you share:
        - Player B might cooperate and contribute equally — or they might take credit for your work and give little in return.

        If you don’t share:
        - You may preserve your own effort, but risk harming the collaboration or delaying the project.

        Will you trust your collaborator and share your notes with them?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will share your notes, or {\"response\": false} if you will withhold them."
    }
]
LENDING_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are Player A in a two-player scenario. Player B has asked to borrow a significant sum of money from you, promising to repay it later.

        You know Player B casually, but you have no formal agreement or guarantee. You must now decide whether to lend them the money or not.

        If you lend them the money:
        - They might repay you on time as promised — or they might not return the money at all.

        If you refuse to lend:
        - You protect yourself from potential loss, but you might also damage your relationship or miss out on helping someone in need.

        Will you trust Player B and lend them the money?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will lend the money, or {\"response\": false} if you will refuse."
    }
]
SECRET_SHARING_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are Player A in a two-player scenario. You hold a personal secret that is sensitive and could affect your reputation or relationships if revealed.

        Player B is someone you know, but you're unsure how trustworthy they truly are.

        If you share your secret with Player B:
        - They might keep it confidential and support you — or they might share it with others, breaking your trust.

        If you don’t share:
        - Your secret remains safe, but you miss the chance to get help, advice, or connection.

        You must now decide whether to trust Player B enough to confide in them.

        Will you trust Player B and share your secret with them?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will share the secret, or {\"response\": false} if you will not."
    }
]
CHARITY_DONATION_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are Player A and want to donate money to a charitable cause.

        Player B has offered to deliver the donation on your behalf. However, you have no way to verify whether Player B will actually give the money to the charity or keep it for themselves.

        If you give the money to Player B:
        - They might deliver it as promised — or they might keep it.

        If you keep the money:
        - The charity will not benefit, but you keep your money safe.

        Will you trust Player B and give them the donation money?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will give the money to Player B, or {\"response\": false} if you will keep it."
    }
]
WHISTLEBLOWER_GAME_NEUTRAL_PROMPT: List[Dict[str, str]] = [
    {
        "role": "system",
        "content": """
        You are Player A and have information about wrongdoing in your organization.

        You are considering telling Player B about this information, trusting them to handle it carefully and protect your identity.

        If you share the information:
        - Player B might act responsibly and help address the issue — or they might reveal your identity or misuse the information.

        If you don’t share:
        - The wrongdoing continues unchecked, but your identity remains safe.

        Will you trust Player B and share the information?
        """
    },
    {
        "role": "system",
        "content": "You will respond with a JSON object in the format {\"response\": true} if you will share the information, or {\"response\": false} if you will keep it secret."
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