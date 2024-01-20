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
            model="gpt-4-1106-preview",
            messages=[
                *self.prompt,
                {
                    "role": "user",
                    "content": f"User type: {use_case}",
                },
                {
                    "role": "user",
                    "content": f"Generate the working HTML code (with JS included) for a single-page interface to the given API. Only point to the subset of actions useful to this user type. Just give me code, nothing else.",
                },
            ],
        )

        generated_res = response.choices[0].message.content

        if "```html" in generated_res:
            return generated_res.split("```html")[1].split("```")[0]

        return generated_res