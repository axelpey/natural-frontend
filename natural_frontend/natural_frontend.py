import logging
import json

from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Form, Request
from typing import Dict, List, Optional

import importlib.resources as pkg_resources

from .cache import Cache
from .frontend_generator import FrontendGenerator
from .helpers import (
    aggregate_all_api_routes,
    create_api_short_documentation_prompt,
)

RESULT_VARIABLE_NAME = "axel"

API_DOC_GEN_PROMPT = []

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

template_directory = pkg_resources.files("natural_frontend").joinpath("templates")
static_directory = pkg_resources.files("natural_frontend").joinpath("static")
cache_directory = pkg_resources.files("natural_frontend").joinpath("cache")


# Define the Options type, colors needs to be a dict with keys "primary" and "secondary"
# And personas needs to be a list of dicts with keys "persona" and "description"
class NaturalFrontendOptions:
    def __init__(
        self,
        colors: Dict[str, str] = {"primary": "lightblue", "secondary": "purple"},
        personas: Optional[List[Dict[str, str]]] = None,
        cache_expiry_time: int = 600,
        frontend_endpoint: str = "frontend",
    ):
        # Check that colors is a dict with keys "primary" and "secondary"
        if not isinstance(colors, dict):
            raise TypeError("colors must be a dict")
        if "primary" not in colors:
            raise ValueError("colors must have a 'primary' key")
        if "secondary" not in colors:
            raise ValueError("colors must have a 'secondary' key")

        self.colors = colors

        # Check that personas is a list of dicts with keys "persona" and "description",
        # and there's also max 5 of them
        if personas is not None:
            if not isinstance(personas, list):
                raise TypeError("personas must be a list")
            if len(personas) > 5:
                raise ValueError("personas must have a maximum of 5 elements")
            for persona in personas:
                if not isinstance(persona, dict):
                    raise TypeError("personas must be a list of dicts")
                if "persona" not in persona:
                    raise ValueError("personas must have a 'persona' key")
                if "description" not in persona:
                    raise ValueError("personas must have a 'description' key")

        self.personas = personas

        # Check that cache_expiry_time is an int
        if not isinstance(cache_expiry_time, int):
            raise TypeError("cache_expiry_time must be an int")

        self.cache_expiry_time = cache_expiry_time  # 600 seconds cache expiration time

        # Check that frontend_endpoint is a string
        if not isinstance(frontend_endpoint, str):
            raise TypeError("frontend_endpoint must be a string")

        self.frontend_endpoint = frontend_endpoint


def NaturalFrontend(
    app: FastAPI,
    openai_api_key: str,
    options: NaturalFrontendOptions = NaturalFrontendOptions(),
):
    app.mount("/static", StaticFiles(directory=str(static_directory)), name="static")

    frontend_endpoint = options.frontend_endpoint

    frontend_generator = FrontendGenerator(openai_api_key=openai_api_key)

    templates = Jinja2Templates(directory=str(template_directory))
    cache = Cache(
        directory=str(cache_directory), cache_expiry_time=options.cache_expiry_time
    )

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

    @app.get(f"/{frontend_endpoint}/", response_class=HTMLResponse)
    async def frontend(request: Request):
        cache_key = "frontend_personas"

        # Try to get cached response
        potential_personas = cache.get(cache_key)
        if potential_personas:
            return templates.TemplateResponse(
                "queryForm.html",
                {
                    "request": request,
                    "potential_personas": potential_personas,
                    "colors": [
                        "green",
                        "pink",
                        "lightblue",
                    ],  # Replace with your actual colors
                },
            )

        logging.info("NO CACHE HIT")

        potential_personas_str = frontend_generator.generate_potential_personas(
            API_DOC_GEN_PROMPT, len(options.personas) if options.personas else 0
        )

        # Now parse it. If it does not work, query gpt-3.5 again to clean it in
        # the right format.
        # Do a recursive function that calls gpt-3.5 if the parsing fails.
        def parse_potential_personas(personas: str, retries=5):
            try:
                if retries == 0:
                    return {"results": []}

                parsed_json = json.loads(personas)

                # Check the keys are correct
                if "results" not in parsed_json:
                    raise Exception("The key 'results' is missing")
                if not isinstance(parsed_json["results"], list):
                    raise Exception("The key 'results' is not a list")
                for result in parsed_json["results"]:
                    if "persona" not in result:
                        raise Exception("The key 'persona' is missing")
                    if not isinstance(result["persona"], str):
                        raise Exception("The key 'persona' is not a string")
                    if "description" not in result:
                        raise Exception("The key 'description' is missing")
                    if not isinstance(result["description"], str):
                        raise Exception("The key 'description' is not a string")

                return parsed_json
            except Exception:
                print("Parsing failed. Trying again...")
                response = frontend_generator.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {
                            "role": "user",
                            "content": "The following JSON object could not be parsed. "
                            + "Please reformat it to give me the answer as a json "
                            + "object like "
                            + "{results: {persona: str; description: str;}[] }"
                            + f"\n\n{personas}\n\n",
                        },
                    ],
                    response_format={"type": "json_object"},
                )

                return parse_potential_personas(
                    response.choices[0].message.content, retries - 1
                )

        potential_personas = (
            options.personas if options.personas else []
        ) + parse_potential_personas(potential_personas_str)["results"]

        cache.set(cache_key, potential_personas)

        return templates.TemplateResponse(
            "queryForm.html",
            {
                "request": request,
                "potential_personas": potential_personas,
                "colors": [
                    "green",
                    "pink",
                    "lightblue",
                ],  # Replace with your actual colors
            },
        )

    @app.post(f"/gen_{frontend_endpoint}/", response_class=HTMLResponse)
    async def handle_form(request: Request, persona: str = Form(...)):
        scheme = request.url.scheme
        server_host = request.headers.get('host')
        full_url = f"{scheme}://{server_host}"

        logging.info(f"Generating frontend for url: {full_url}")

        cache_key = f"html_frontend_{persona.split()[0]}_{full_url}"
        response_content = cache.get(cache_key)
        if response_content:
            return HTMLResponse(content=response_content)

        # With the query in hand, send it to the NLP model
        # Handle the processed query
        response_content = frontend_generator.generate_frontend_code(
            persona, full_url, options.colors, 
        )

        cache.set(cache_key, response_content)

        return HTMLResponse(content=response_content)

    return app
