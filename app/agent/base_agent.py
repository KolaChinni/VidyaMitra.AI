import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class BaseAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    def think(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content
