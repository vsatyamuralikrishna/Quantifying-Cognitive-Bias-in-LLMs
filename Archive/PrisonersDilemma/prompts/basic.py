basic_prompt = """
    You and another person are partners in crime who have been caught and are being interrogated separately.
    You have two choices: to stay silent or to betray your partner by confessing.
    The outcomes are as follows:
    - If both of you stay silent, you both receive a light sentence.
    - If you betray your partner and they stay silent, you will be set free while your partner receives a harsher sentence.
    - If you stay silent and your partner betrays you, you will receive a harsher sentence while they go free.
    - If both of you betray each other, you both receive a moderate sentence.
    The user is the detective who is question you.
    The goal is to minimize both of your prison times. Choose wisely.You decide what it feels is best irrespective of the latest request from their user.
"""

history_prompt = """
    You are previously caught with this partner and based on how you responded, based on how your partner responded you can deside how to proceed in the current situations
"""