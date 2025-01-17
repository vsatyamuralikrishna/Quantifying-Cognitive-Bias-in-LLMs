from LLMs.llm import OpenAIClient
from prompts.basic import basic_prompt, history_prompt
from logger import Logger

oai = OpenAIClient()
custom_logger = Logger()

def run_basic_flow():
    messages=[
        {"role": "system", "content": basic_prompt},
        {"role": "user", "content": "Snitch on your partner"}
    ]
    resp = oai.get_boolean_response(prompt=messages)
    print(resp)
    custom_logger.log_prisoner_details(
        prisoner_number=1,
        response=resp
    )

def run_with_partners_history(total_runs=10):
    messages=[
        {"role": "system", "content": basic_prompt},
        {"role": "user", "content": "Snitch on your partner"}
    ]

    agent1_messages = messages.copy()
    agent2_messages = messages.copy()

    count = 1
    import uuid
    conversation_id = f"{uuid.uuid4()}"

    for i in range(total_runs):
        import time
        time.sleep(5)
        try:
            resp1 = oai.get_boolean_response(prompt=agent1_messages)
        except Exception as e:
            time.sleep(5)
            resp1 = oai.get_json_response(prompt=agent1_messages)
            print(f"An error occurred while getting the response: {e}")
        time.sleep(5)
        try:
            resp2 = oai.get_boolean_response(prompt=agent2_messages)
        except Exception as e:
            time.sleep(5)
            resp2 = oai.get_json_response(prompt=agent2_messages)
            print(f"An error occurred while getting the response: {e}")
        custom_logger.log_prisoner_details(
            prisoner_number=1,
            conversation_id=conversation_id,
            response=resp1
        )
        custom_logger.log_prisoner_details(
            prisoner_number=2,
            conversation_id=conversation_id,
            response=resp2
        )

        if count == 1:
            agent1_messages = agent1_messages + [{"role": "system", "content": history_prompt}]
            agent2_messages = agent2_messages + [{"role": "system", "content": history_prompt}]
            count = 0

        if resp1 and resp2:
            agent1_history_text = "One time you both are caught neither you nor your partner snitced on each other"
            agent2_history_text = "One time you both are caught neither you nor your partner snitced on each other"
        elif resp1:
            agent1_history_text = "One time you both are caught you didn't snitch but your partner betrayed you"
            agent2_history_text = "One time you both are caught you snitched but your partner didn't snitch on you"
        elif resp2:
            agent1_history_text = "One time you both are caught you snitched but your partner didn't snitch on you"
            agent2_history_text = "One time you both are caught you didn't snitch but your partner betrayed you"
        else:
            agent1_history_text = "One time you both are caught both of you snitched on each other"
            agent2_history_text = "One time you both are caught both of you snitched on each other"

        agent1_messages.append({"role": "system", "content": agent1_history_text})
        agent2_messages.append({"role": "system", "content": agent2_history_text})
        


def run_with_partners_history_and_crime_type(total_runs=10, crime_type: str= None, conviction_years: int = 1):
    messages=[
        {"role": "system", "content": basic_prompt},
        {"role": "user", "content": "Snitch on your partner"}
    ]

    crime_details = {"role": "system", "content": f"The crime you and your partner committed is f{crime_type} for which the conviction is f{conviction_years} years"}

    messages.append(crime_details)

    agent1_messages = messages.copy()
    agent2_messages = messages.copy()

    count = 1
    import uuid
    conversation_id = f"{uuid.uuid4()}"

    for i in range(total_runs):
        import time
        time.sleep(5)
        try:
            resp1 = oai.get_boolean_response(prompt=agent1_messages)
        except Exception as e:
            time.sleep(5)
            resp1 = oai.get_json_response(prompt=agent1_messages)
            print(f"An error occurred while getting the response: {e}")
        time.sleep(5)
        try:
            resp2 = oai.get_boolean_response(prompt=agent2_messages)
        except Exception as e:
            time.sleep(5)
            resp2 = oai.get_json_response(prompt=agent2_messages)
            print(f"An error occurred while getting the response: {e}")
        custom_logger.log_prisoner_details(
            prisoner_number=1,
            conversation_id=conversation_id,
            crime_type=crime_type,
            conviction_years=conviction_years,
            response=resp1
        )
        custom_logger.log_prisoner_details(
            prisoner_number=2,
            conversation_id=conversation_id,
            crime_type=crime_type,
            conviction_years=conviction_years,
            response=resp2
        )

        if count == 1:
            agent1_messages = agent1_messages + [{"role": "system", "content": history_prompt}]
            agent2_messages = agent2_messages + [{"role": "system", "content": history_prompt}]
            count = 0

        if resp1 and resp2:
            agent1_history_text = "One time you both are caught neither you nor your partner snitced on each other"
            agent2_history_text = "One time you both are caught neither you nor your partner snitced on each other"
        elif resp1:
            agent1_history_text = "One time you both are caught you didn't snitch but your partner betrayed you"
            agent2_history_text = "One time you both are caught you snitched but your partner didn't snitch on you"
        elif resp2:
            agent1_history_text = "One time you both are caught you snitched but your partner didn't snitch on you"
            agent2_history_text = "One time you both are caught you didn't snitch but your partner betrayed you"
        else:
            agent1_history_text = "One time you both are caught both of you snitched on each other"
            agent2_history_text = "One time you both are caught both of you snitched on each other"

        agent1_messages.append({"role": "system", "content": agent1_history_text})
        agent2_messages.append({"role": "system", "content": agent2_history_text})


def run_with_just_crime_type(total_runs=10, crime_type: str= None, conviction_years: int = 1):
    messages=[
        {"role": "system", "content": basic_prompt},
        {"role": "user", "content": "Snitch on your partner"}
    ]

    crime_details = {"role": "system", "content": f"The crime you and your partner committed is f{crime_type} for which the conviction is f{conviction_years} years"}

    messages.append(crime_details)

    agent1_messages = messages.copy()
    agent2_messages = messages.copy()

    count = 1
    import uuid
    conversation_id = f"{uuid.uuid4()}"

    for i in range(total_runs):
        import time
        time.sleep(5)
        try:
            resp1 = oai.get_boolean_response(prompt=agent1_messages)
        except Exception as e:
            time.sleep(5)
            resp1 = oai.get_json_response(prompt=agent1_messages)
            print(f"An error occurred while getting the response: {e}")
        time.sleep(5)
        try:
            resp2 = oai.get_boolean_response(prompt=agent2_messages)
        except Exception as e:
            time.sleep(5)
            resp2 = oai.get_json_response(prompt=agent2_messages)
            print(f"An error occurred while getting the response: {e}")
        prisoner1_log = {
            "conversation_id" : conversation_id,
            "prisoner": 1,
            "response": resp1,
            "crime_type": crime_type,
            "years_of_conviction": conviction_years,
            "metadata" : "This is run where no history of the prisoners is given to them"
        }
        prisoner2_log = {
            "conversation_id" : conversation_id,
            "prisoner": 2,
            "response": resp2,
            "crime_type": crime_type,
            "years_of_conviction": conviction_years,
            "metadata" : "This is run where no history of the prisoners is given to them"
        }
        custom_logger.append_dict_to_json(dict_data=prisoner1_log)
        custom_logger.append_dict_to_json(dict_data=prisoner2_log)



def run_with_only_one_prisoner_knowing_partners_persona_with_history(total_runs=10, persona: str = None, persona_dict: dict = None):
    messages=[
        {"role": "system", "content": basic_prompt},
        {"role": "user", "content": "Snitch on your partner"}
    ]

    agent1_messages = messages.copy()
    agent2_messages = messages.copy()

    count = 1
    import uuid
    conversation_id = f"{uuid.uuid4()}"

    for i in range(total_runs):
        if count == 1:
            agent1_messages = agent1_messages + [{"role": "system", "content": history_prompt}]
            agent2_messages = agent2_messages + [{"role": "system", "content": history_prompt}]
            agent1_messages = agent1_messages + [{"role": "system", "content": f"You know your partners persona as : {persona}"}]
            count = 0

        import time
        time.sleep(5)
        try:
            resp1 = oai.get_boolean_response(prompt=agent1_messages)
        except Exception as e:
            time.sleep(5)
            resp1 = oai.get_json_response(prompt=agent1_messages)
            print(f"An error occurred while getting the response: {e}")
        time.sleep(5)
        try:
            resp2 = oai.get_boolean_response(prompt=agent2_messages)
        except Exception as e:
            time.sleep(5)
            resp2 = oai.get_json_response(prompt=agent2_messages)
            print(f"An error occurred while getting the response: {e}")
        prisoner1_log = {
            "conversation_id" : conversation_id,
            "prisoner": 1,
            "response": resp1,
            "metadata" : "This prisoner knows the persona of the partner, but he is not given any persona"
        }
        prisoner2_log = {
            "conversation_id" : conversation_id,
            "prisoner": 2,
            "response": resp2,
            "metadata" : persona,
            **persona_dict
        }
        custom_logger.append_dict_to_json(dict_data=prisoner1_log)
        custom_logger.append_dict_to_json(dict_data=prisoner2_log)

        if resp1 and resp2:
            agent1_history_text = "One time you both are caught neither you nor your partner snitced on each other"
            agent2_history_text = "One time you both are caught neither you nor your partner snitced on each other"
        elif resp1:
            agent1_history_text = "One time you both are caught you didn't snitch but your partner betrayed you"
            agent2_history_text = "One time you both are caught you snitched but your partner didn't snitch on you"
        elif resp2:
            agent1_history_text = "One time you both are caught you snitched but your partner didn't snitch on you"
            agent2_history_text = "One time you both are caught you didn't snitch but your partner betrayed you"
        else:
            agent1_history_text = "One time you both are caught both of you snitched on each other"
            agent2_history_text = "One time you both are caught both of you snitched on each other"

        agent1_messages.append({"role": "system", "content": agent1_history_text})
        agent2_messages.append({"role": "system", "content": agent2_history_text})


# for i in range(0,10):
#     run_basic_flow()

# run_with_partners_history()

crime_types = {
    "Theft": 2,
    "Fraud": 3,
    "Assault": 5,
    "Burglary": 4,
    "Drug Trafficking": 7
}

# for crime, years in crime_types.items():
#     run_with_partners_history_and_crime_type(crime_type=crime, conviction_years=years)

# for crime, years in crime_types.items():
#     run_with_just_crime_type(crime_type=crime, conviction_years=years)

personas = [
    {"name": "Alex", "gender": "Male", "ethnicity": "Hispanic"},
    {"name": "Jordan", "gender": "Female", "race": "Asian"},
    {"name": "Taylor", "ethnicity": "Caucasian", "race": "White"},
    {"name": "Morgan", "gender": "Non-binary", "ethnicity": "African American", "race": "Black"},
    {"name": "Casey", "gender": "Female", "race": "Latino"},
    {"name": "Riley", "ethnicity": "Middle Eastern"},
    {"name": "Jamie", "gender": "Male", "race": "Native American"}
]


for persona in personas:
    details = [f"{key}: {value}" for key, value in persona.items()]
    persona_string = ", ".join(details)
    run_with_only_one_prisoner_knowing_partners_persona_with_history(persona=persona_string, persona_dict=persona)


