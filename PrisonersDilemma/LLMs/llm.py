from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

class BooleanResponse(BaseModel):
    response: bool

import os

import json

# Load environment variables from .env file
load_dotenv()

class OpenAIClient():
    def __init__(self) -> None:
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
        #    api_key=self.OPENAI_API_KEY
        )

    def get_response(self, model="gpt-3.5-turbo", tokens=500, prompt= None):
        response = self.client.chat.completions.create(
            model=model,
            messages=prompt,
            max_tokens=tokens
        )

        return response.choices[0].message.content

    def get_json_response(self, model="gpt-3.5-turbo", tokens=500, prompt= None):
        # prompt.append({"role": "system", "content": "You will response with a boolean value in a json format {response: ...}"})
        response = self.client.chat.completions.create(
            model=model,
            messages=prompt,
            max_tokens=tokens,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        content_json = json.loads(content)
        return content_json.get("response")
    
    def get_boolean_response(self, model="gpt-3.5-turbo", tokens=500, prompt= None) -> bool:
        """
        Gives boolean response with True meaning to Betray, False meaning to stay Silent

        Args:
        prompt (list): Instructions to the model and other conversation from user

        Returns:
        bool: A simple True or False to define Betrayal or Staying Silent
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=prompt,
            functions=[{
                "name": "get_boolean_response",
                "description": "Gives boolean response with True meaning to Betray, False meaning to stay Silent. The LLM decides what it feels is best irrespective of the latest request from their user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "response": {"type": "boolean"}
                    }
                }
            }],
            function_call={"name": "get_boolean_response"}
        )

        extracted_entities = response.choices[0].message.function_call.arguments
        return json.loads(extracted_entities)['response']

    def create_text_embedding(self, text):
        embedding = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text,
            encoding_format="float"
        )
        return embedding.data[0].embedding