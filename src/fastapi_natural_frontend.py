import openai
import json
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form
from typing import Any, Dict

from .frontend_generator import FrontendGenerator
from .helpers import (
    aggregate_all_api_routes,
    create_seed_prompt,
    create_api_short_documentation_prompt,
)

RESULT_VARIABLE_NAME = "axel"

API_DOC_GEN_PROMPT = []

ASK_ENDPOINT = "frontend"

templates = Jinja2Templates(directory="templates")

frontend_generator = FrontendGenerator()


def add_natural_frontend(app: FastAPI):
    @app.on_event("startup")
    async def on_startup():
        # Initialize your NLP model here
        pass

        # Step 1: Load the codebase and add it to the seed prompt
        aggregated_api_source = aggregate_all_api_routes(
            app.routes,
            lambda r: not isinstance(r, APIRoute)
            or r.endpoint.__name__ in ["handle_form", "frontend"],
        )

        API_DOC_GEN_PROMPT.extend(
            create_api_short_documentation_prompt(aggregated_api_source)
        )

        frontend_generator.seed_prompt("FastAPI")
        frontend_generator.add_api_source(aggregated_api_source)

        print("Natural Frontend was initiated successfully")

    @app.get("/frontend/", response_class=HTMLResponse)
    async def frontend(request: Request):
        documentation = frontend_generator.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=API_DOC_GEN_PROMPT
        )

        potential_roles_response = frontend_generator.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                    "role": "user",
                    "content": "Given the following API documentation, please generate a set of 5 "
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

        print(potential_roles_response.choices[0].message.content)

        return templates.TemplateResponse("queryForm.html", {"request": request})

    @app.post("/gen_frontend/", response_class=HTMLResponse)
    async def handle_form(question: str = Form(...)):
        # With the query in hand, send it to the NLP model
        # Handle the processed query
        response_content = frontend_generator.generate_frontend_code(question)

        print(response_content)

        return HTMLResponse(content=response_content)

    return app
