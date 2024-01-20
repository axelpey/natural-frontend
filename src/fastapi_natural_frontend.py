import openai
import json
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from typing import Any, Dict

from .helpers import aggregate_all_api_routes, create_seed_prompt

RESULT_VARIABLE_NAME = "axel"

SEED_PROMPT = create_seed_prompt("FastApi", "Python", RESULT_VARIABLE_NAME, "zorglub")

ASK_ENDPOINT = "ask"

templates = Jinja2Templates(directory="templates")

# Load OpenAI key from creds.json
with open("creds.json") as f:
    creds = json.load(f)
    if not "key" in creds:
        raise RuntimeError("Please provide your OpenAI token in creds.json as 'key'")

client = openai.OpenAI(api_key=creds["key"])


def add_natural_frontend(app: FastAPI):
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

        print("Natural Frontend was initiated successfully")

    @app.get("/frontend/", response_class=HTMLResponse)
    async def frontend(request: Request):
        return templates.TemplateResponse("queryForm.html", {"request": request})


    @app.get("/gen_frontend/")
    async def generate_frontend() -> Dict[str, Any]:
        # With the query in hand, send it to the NLP model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                *SEED_PROMPT,
                {
                    "role": "user",
                    "content": f"Generate a frontend for this API",
                },
            ],
        )

        frontend_code = response.choices[0].message.content

        def generate_frontend_code(frontend_code):
            return "REACT CODE EMBEDDED IN AN HTML PAGE WITH A SCRIPT TAG AND MINIFIED REACT BASE"

        # Handle the processed query
        # response = handle_processed_query(processed_query)
        response = generate_frontend_code(frontend_code)
        return response

    return app
