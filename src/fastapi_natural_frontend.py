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

    @app.post("/gen_frontend/", response_class=HTMLResponse)
    async def handle_form(question: str = Form(...)):
        # FIXME: This is a hack to get the frontend code
        if False:
            # With the query in hand, send it to the NLP model
            frontend_code = frontend_generator.generate_frontend_code(SEED_PROMPT)

            def generate_frontend_code(frontend_code):
                return "REACT CODE EMBEDDED IN AN HTML PAGE WITH A SCRIPT TAG AND MINIFIED REACT BASE"

            # Handle the processed query
            response_content = generate_frontend_code(frontend_code)

        response_content = f"<html><body><h2>You asked: {question}</h2></body></html>"
        return HTMLResponse(content=response_content)

    return app
