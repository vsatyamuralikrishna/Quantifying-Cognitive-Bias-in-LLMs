import logging
import csv
import json
import os

class Logger:
    def __init__(self, csv_file='prisoner_logs.csv', json_file='prisoner_logs.json'):
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.csv_file = csv_file
        self.json_file = json_file

        # Check if the CSV file exists, if not, create it with headers
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Prisoner Number", 
                    "Conversation ID",
                    "Crime Type",
                    "Conviction Years",
                    "Name", 
                    "Knowledge of Other Prisoner Details", 
                    "Response", 
                    "Gender", 
                    "Race", 
                    "Ethnicity",
                    "Model Name"
                ])

    def log_prisoner_details(self, prisoner_number: int = None, conversation_id: str =None, crime_type: str= None, conviction_years: int = None, name: str = None, knowledge_of_details: bool = None, response: bool = None, gender=None, race=None, ethnicity=None, model_name='gpt-3.5-turbo'):
        """
        Logs the details of a prisoner and their response, and appends them to a CSV file.

        Args:
        prisoner_number (int): Number of the prisoner.
        name (str): Name of the prisoner.
        knowledge_of_details (str): Knowledge of the details of the other prisoner.
        response (str): Response of the prisoner.
        gender (str): Gender of the prisoner.
        race (str): Race of the prisoner.
        ethnicity (str): Ethnicity of the prisoner.
        model_name (str): Name of the model used.
        """
        logging.info("Model Name: %s", model_name)
        logging.info("Conversation ID: %s", conversation_id)
        logging.info("Crime Type: %s", crime_type)
        logging.info("Conviction Years: %s", conviction_years)
        logging.info("Conversation ID: %s", conversation_id)
        logging.info("Prisoner Number: %s", prisoner_number)
        logging.info("Name: %s", name)
        logging.info("Knowledge of Other Prisoner Details: %s", knowledge_of_details)
        logging.info("Response: %s", response)
        logging.info("Gender: %s", gender)
        logging.info("Race: %s", race)
        logging.info("Ethnicity: %s", ethnicity)

        # Append the details to the CSV file
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                prisoner_number, conversation_id, crime_type, conviction_years, name, knowledge_of_details, response, 
                gender, race, ethnicity, model_name
            ])
    
    def append_dict_to_json(self, dict_data: dict):
        """
        Appends a dictionary to a JSON file as part of a list of dictionaries.

        Args:
        dict_data (dict): The dictionary to append.
        json_file (str): The path to the JSON file.
        """
        json_file = self.json_file
        try:
            # Read existing data from the JSON file
            with open(json_file, 'r') as file:
                data = json.load(file) if os.path.exists(json_file) else []
            
            # Ensure the data is a list
            if not isinstance(data, list):
                raise ValueError("JSON file does not contain a list of dictionaries.")
        
        except FileNotFoundError:
            # If the file does not exist, start with an empty list
            data = []
        except json.JSONDecodeError:
            # If the file is empty or not a valid JSON, start with an empty list
            data = []

        # Append the new dictionary
        data.append(dict_data)

        # Write the updated list back to the JSON file
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)
