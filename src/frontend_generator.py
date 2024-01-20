import json

from openai import OpenAI

class FrontendGenerator:
    def __init__(self):
        with open("creds.json") as f:
            creds = json.load(f)
            if not "key" in creds:
                raise RuntimeError("Please provide your OpenAI token in creds.json as 'key'")
        self.client = OpenAI(api_key=creds["key"])
        self.prompt = []

    def seed_prompt(
        self,
        framework_name: str
    ):
        self.prompt.append(
            {
                "role": "system",
                "content": f"You will be given a {framework_name} codebase for an API and a user type with a specific use case."
            }
        )

    def add_api_source(self, api_source):
        self.prompt.append(
            {
                "role": "system",
                "content": f"Codebase: \n{api_source}\n"
            }
        )

    def generate_frontend_code(self, use_case):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                *self.prompt,
                {
                    "role": "user",
                    "content": f"User type: {use_case}",
                },
                {
                    "role": "user",
                    "content": f"Generate a simple HTML frontend interface to this API tailored to this user type (a form page, for instance). GIVE ME ONLY HTML CODE, NOTHING ELSE.",
                },
            ],
        )

        return response.choices[0].message.content