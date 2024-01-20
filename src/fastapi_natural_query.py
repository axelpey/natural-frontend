import openai
import json
from fastapi.routing import APIRoute
from fastapi import FastAPI
from typing import Any, Dict
import asyncio
import nest_asyncio

nest_asyncio.apply()

from .helpers import aggregate_all_api_routes, create_seed_prompt

RESULT_VARIABLE_NAME = "axel"

SEED_PROMPT = create_seed_prompt("FastApi", "Python", RESULT_VARIABLE_NAME, "zorglub")

ASK_ENDPOINT = "ask"

# Load OpenAI key from creds.json
with open("creds.json") as f:
    creds = json.load(f)
    if not "key" in creds:
        raise RuntimeError("Please provide your OpenAI token in creds.json as 'key'")

client = openai.OpenAI(api_key=creds["key"])


def add_nlp_query_route(app: FastAPI):
    @app.on_event("startup")
    async def on_startup():
        # Initialize your NLP model here
        pass

        # Step 1: Load the codebase and add it to the seed prompt

        aggregated_api_source = aggregate_all_api_routes(
            app.routes,
            lambda r: not isinstance(r, APIRoute)
            or r.endpoint.__name__ == ASK_ENDPOINT,
        )

        SEED_PROMPT.append({"role": "user", "content": aggregated_api_source})

        print("Natural Query was initiated successfully")

    @app.get("/ask/{query}")
    async def ask(query: str) -> Dict[str, Any]:
        # Step 2: Load the model
        # Load GPT-3.5
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                *SEED_PROMPT,
                {
                    "role": "user",
                    "content": f"What's the code equivalent of this query: {query}",
                },
            ],
        )

        code = response.choices[0].message.content

        api_routes = {route.name: route.endpoint for route in app.routes}

        axel = ""

        def exec_code(code):
            async def zorglub(route_name, params={}):
                await api_routes[route_name](**params)

            s = f"""
global result, async_exec_coro
async def async_exec():
    global result
    {code}
async_exec_coro = async_exec()
            """

            print(s)

            exec(s, globals(), locals())

            loop = asyncio.get_event_loop()
            loop.run_until_complete(async_exec_coro)

            return result

        print(exec_code('zorglub("get_books")'))
        return {}

        print(code)

        exec(code)

        print(axel)

        # Handle the processed query
        # response = handle_processed_query(processed_query)
        response = {"prompt": response.choices[0].message.content, "result": ""}
        return response

    return app
