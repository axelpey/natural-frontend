import json

import openai

class FrontendGenerator:
    def __init__(self):
        with open("creds.json") as f:
            creds = json.load(f)
            if not "key" in creds:
                raise RuntimeError("Please provide your OpenAI token in creds.json as 'key'")
        self.client = openai.OpenAI(api_key=creds["key"])
        self.prompt = []

    def seed_prompt(
        self,
        framework_name: str
    ):
        self.prompt.append(
            {
                "role": "system",
                "content": f"You will be given a {framework_name} codebase."
            }
        )

    def add_api_source(self, api_source):
        self.prompt.append(
            {
                "role": "system",
                "content": api_source
            }
        )

    def generate_frontend_code(self, question):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                *self.prompt,
                {
                    "role": "user",
                    "content": f"Generate a simple HTML frontend code for this API. Don't import any module. GIVE ME ONLY CODE, NOTHING ELSE.",
                },
            ],
        )

        return response.choices[0].message.content