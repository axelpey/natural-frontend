import logging
import json

from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI, Form, Request
from typing import Dict, List

from .cache import Cache
from .frontend_generator import FrontendGenerator
from .helpers import (
    aggregate_all_api_routes,
    create_api_short_documentation_prompt,
)

RESULT_VARIABLE_NAME = "axel"

API_DOC_GEN_PROMPT = []

ASK_ENDPOINT = "frontend"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

templates = Jinja2Templates(directory="natural_frontend/templates")

cache = Cache()

# Define the Options type, colors needs to be a dict with keys "primary" and "secondary"
# And personas needs to be a list of dicts with keys "persona" and "description"
class NaturalFrontendOptions:
    def __init__(
        self,
        colors: Dict[str, str] = {"primary": "lightblue", "secondary": "purple"},
        personas: List[Dict[str, str]] = None,
    ):
        # Check that colors is a dict with keys "primary" and "secondary"
        if colors is not None:
            if not isinstance(colors, dict):
                raise TypeError("colors must be a dict")
            if not "primary" in colors:
                raise ValueError("colors must have a 'primary' key")
            if not "secondary" in colors:
                raise ValueError("colors must have a 'secondary' key")

        self.colors = colors

        # Check that personas is a list of dicts with keys "persona" and "description", and there's also max 5 of them
        if personas is not None:
            if not isinstance(personas, list):
                raise TypeError("personas must be a list")
            if len(personas) > 5:
                raise ValueError("personas must have a maximum of 5 elements")
            for persona in personas:
                if not isinstance(persona, dict):
                    raise TypeError("personas must be a list of dicts")
                if not "persona" in persona:
                    raise ValueError("personas must have a 'persona' key")
                if not "description" in persona:
                    raise ValueError("personas must have a 'description' key")

        self.personas = personas


def NaturalFrontend(
    app: FastAPI, openai_api_key: str, options: NaturalFrontendOptions = NaturalFrontendOptions()
):
    app.mount("/static", StaticFiles(check_dir=False, directory="natural_frontend/static", packages=[("natural_frontend", "static")]), name="static")

    frontend_generator = FrontendGenerator(openai_api_key=openai_api_key)

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
    async def frontend(request: Request, cache: Cache = Depends()):
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
        
        potential_personas_str = frontend_generator.generate_potential_personas(API_DOC_GEN_PROMPT, len(options.personas) if options.personas else 0)

        # Now parse it. If it does not work, query gpt-3.5 again to clean it in the right format.
        # Do a recursive function that calls gpt-3.5 if the parsing fails.
        def parse_potential_personas(personas: str, retries=5):
            try:
                if retries == 0:
                    return {"results": []}

                parsed_json = json.loads(personas)

                # Check the keys are correct
                if not "results" in parsed_json:
                    raise Exception("The key 'results' is missing")
                if not isinstance(parsed_json["results"], list):
                    raise Exception("The key 'results' is not a list")
                for result in parsed_json["results"]:
                    if not "persona" in result:
                        raise Exception("The key 'persona' is missing")
                    if not isinstance(result["persona"], str):
                        raise Exception("The key 'persona' is not a string")
                    if not "description" in result:
                        raise Exception("The key 'description' is missing")
                    if not isinstance(result["description"], str):
                        raise Exception("The key 'description' is not a string")

                return parsed_json
            except:
                print("Parsing failed. Trying again...")
                response = frontend_generator.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {
                            "role": "user",
                            "content": "The following JSON object could not be parsed. "
                            + "Please reformat it to give me the answer as a json object like {results: {persona: str; description: str;}[] }"
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

    @app.post("/gen_frontend/", response_class=HTMLResponse)
    async def handle_form(persona: str = Form(...)):
        cache_key = f"html_frontend_{persona.split()[0]}"
        response_content = cache.get(cache_key)
        if response_content:
            return HTMLResponse(content=response_content)

        # With the query in hand, send it to the NLP model
        # Handle the processed query
        response_content = frontend_generator.generate_frontend_code(
            persona, options.colors
        )

        cache.set(cache_key, response_content)

        return HTMLResponse(content=response_content)

    return app
