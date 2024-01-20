import json

import openai

class FrontendGenerator:
    def __init__(self):
        with open("creds.json") as f:
            creds = json.load(f)
            if not "key" in creds:
                raise RuntimeError("Please provide your OpenAI token in creds.json as 'key'")
        self.client = openai.OpenAI(api_key=creds["key"])

    def generate_frontend_code(self, seeded_prompt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                *seeded_prompt,
                {
                    "role": "user",
                    "content": f"Generate a frontend for this API",
                },
            ],
        )

        return response.choices[0].message.content