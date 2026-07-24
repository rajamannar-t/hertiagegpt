"""
llm.py

Handles communication with the Groq LLM.

Author: Sai Raja
Project: HeritageGPT
"""

import logging
from openai import OpenAI
from config import Config


class LLM:

    def __init__(self):

        self.client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = Config.MODEL_NAME

    ##########################################################

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ):
        """
        Generate response using Groq.
        """

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": "You are HeritageGPT."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=temperature,

                max_tokens=max_tokens

            )

            answer = response.choices[0].message.content

            return answer

        except Exception as e:

            logging.error(e)

            return f"Error: {e}"