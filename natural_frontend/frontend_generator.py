from openai import OpenAI


class FrontendGenerator:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.prompt = []

    def seed_prompt(self, framework_name: str):
        self.prompt.append(
            {
                "role": "system",
                "content": f"You will be given a {framework_name} codebase for an API and a user type with a specific use case.",
            }
        )

    def add_api_source(self, api_source):
        self.prompt.append({"role": "system", "content": f"Codebase: \n{api_source}\n"})

    def generate_potential_personas(
        self, generated_api_doc, already_generated_persona_num=5
    ):
        documentation = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=generated_api_doc
        )

        potential_personas_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                    "role": "user",
                    "content": f"Given the following API documentation, please generate a set of {5 - already_generated_persona_num} "
                    + "simple user personas that a typical user of this API might fit into. "
                    + "These personas should help in understanding the diverse needs and backgrounds "
                    + "of the users, allowing for the development of a customized frontend interface "
                    + "that caters to their specific requirements and interests."
                    + " Limit each description to 10 words and return as a json object like {results: {persona: str; description: str;}[] }"
                    + "\n\nAPI Documentation;\n\n"
                    + documentation.choices[0].message.content,
                },
            ],
            response_format={"type": "json_object"},
        )

        return potential_personas_response.choices[0].message.content

    def generate_frontend_code(self, use_case, colors=None):
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
                    "content": f"Generate the working HTML code (with JS included) for a single-page interface to the given API. "
                    + "The base url is localhost:80."
                    + "Only point to the subset of actions useful to this user type. "
                    + "Style the interface like you have some real design skills, this is 2024! "
                    + (f"Also use this color scheme: {colors}. " if colors else "")
                    + "Just give me code, nothing else.",
                },
            ],
        )

        generated_res = response.choices[0].message.content

        if "```html" in generated_res:
            return generated_res.split("```html")[1].split("```")[0]

        return generated_res
