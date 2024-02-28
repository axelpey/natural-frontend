import importlib.resources as pkg_resources
import logging
from typing import Annotated, Any, Dict, List, Optional

from .cache import Cache
from .constants import FAST_API, FLASK
from .frontend_generator import FrontendGenerator
from .helpers import (
    aggregate_all_api_routes,
    create_api_short_documentation_prompt,
    get_framework_name_or_crash,
)

RESULT_VARIABLE_NAME = "axel"

API_DOC_GEN_PROMPT = []

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

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
    app: Any,
    openai_api_key: str,
    options: NaturalFrontendOptions = NaturalFrontendOptions(),
):
    framework_name = get_framework_name_or_crash(app)
    logging.info(f"Framework detected: {framework_name}")

    template_directory = pkg_resources.files("natural_frontend").joinpath("templates")
    static_directory = pkg_resources.files("natural_frontend").joinpath("static")
    cache_directory = pkg_resources.files("natural_frontend").joinpath("cache")

    if framework_name == FAST_API:
        from starlette.responses import HTMLResponse
        from starlette.templating import Jinja2Templates
        from starlette.staticfiles import StaticFiles
        from starlette.requests import Request

        from fastapi import Form

        app.mount(
            "/static_nf", StaticFiles(directory=str(static_directory)), name="static_nf"
        )

    elif framework_name == FLASK:
        from flask import request, make_response
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        class Jinja2Templates:
            def __init__(self, directory: str):
                self.directory = directory
                self.env = Environment(
                    loader=FileSystemLoader(self.directory),
                    autoescape=select_autoescape(['html', 'xml'])
                )
            
            def TemplateResponse(self, template_name: str, context: dict):
                """Renders a template and returns a Flask response.
                
                Args:
                    template_name (str): The name of the template file.
                    context (dict): A dictionary of context variables to pass to the template.
                    
                Returns:
                    A Flask response object with the rendered template.
                """
                # Using Flask's render_template function directly can also work,
                # but here we demonstrate using Jinja2's Environment for learning purposes.
                template = self.env.get_template(template_name)
                html_content = template.render(context)
                return make_response(html_content)

    frontend_endpoint = options.frontend_endpoint

    frontend_generator = FrontendGenerator(openai_api_key=openai_api_key)

    templates = Jinja2Templates(directory=str(template_directory))
    cache = Cache(
        directory=str(cache_directory), cache_expiry_time=options.cache_expiry_time
    )

    def initiate_natural_frontend(app: Any, framework_name: str):
        # Step 1: Load the codebase and add it to the seed prompt
        aggregated_api_source = aggregate_all_api_routes(app, framework_name)

        API_DOC_GEN_PROMPT.extend(
            create_api_short_documentation_prompt(aggregated_api_source)
        )

        frontend_generator.seed_prompt(framework_name)
        frontend_generator.add_api_source(aggregated_api_source)

        logging.info("Natural Frontend was initiated successfully")

    if framework_name == FAST_API:

        @app.on_event("startup")
        async def on_startup():
            initiate_natural_frontend(app, framework_name)

    elif framework_name == FLASK:
        with app.app_context():
            initiate_natural_frontend(app, framework_name)

    def render_frontend_template(
        potential_personas: List[Dict[str, str]],
        frontend_endpoint: str,
        request: Request,
    ):
        if framework_name == FAST_API:
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
                    "frontend_endpoint": frontend_endpoint,
                },
            )
        elif framework_name == FLASK:
            return templates.get_template("queryForm.html").render(
                potential_personas=potential_personas,
                colors=[
                    "green",
                    "pink",
                    "lightblue",
                ],
                frontend_endpoint=frontend_endpoint,
            )

    def frontend(request: Optional[Request] = None):
        cache_key = "frontend_personas"

        # Try to get cached response
        potential_personas = cache.get(cache_key)
        if potential_personas:
            return render_frontend_template(
                potential_personas, frontend_endpoint, request
            )

        logging.info("NO CACHE HIT")

        potential_personas_str = frontend_generator.generate_potential_personas(
            API_DOC_GEN_PROMPT, len(options.personas) if options.personas else 0
        )

        # Now parse it. If it does not work, query gpt-3.5 again to clean it in
        # the right format.
        potential_personas = [{"persona": "test", "description": "test"}]

        potential_personas = (
            options.personas if options.personas else []
        ) + frontend_generator.parse_potential_personas(potential_personas_str)[
            "results"
        ]

        cache.set(cache_key, potential_personas)

        return render_frontend_template(potential_personas, frontend_endpoint, request)

    def generate_frontend(persona: str, full_url: str):
        cache_key = f"html_frontend_{persona.split()[0]}_{full_url}"
        response_content = cache.get(cache_key)
        if response_content:
            return HTMLResponse(content=response_content) if framework_name == FAST_API else make_response(response_content)

        # With the query in hand, send it to the NLP model
        # Handle the processed query
        response_content = frontend_generator.generate_frontend_code(
            persona, full_url, options.colors
        )

        cache.set(cache_key, response_content)

        return HTMLResponse(content=response_content) if framework_name == FAST_API else make_response(response_content)

    if framework_name == FAST_API:

        async def fast_api_frontend(request: Request):
            cache_key = "frontend_personas"

            # Try to get cached response
            potential_personas = cache.get(cache_key)
            if potential_personas:
                return render_frontend_template(
                    potential_personas, frontend_endpoint, request
                )

            logging.info("NO CACHE HIT")

            potential_personas_str = frontend_generator.generate_potential_personas(
                API_DOC_GEN_PROMPT, len(options.personas) if options.personas else 0
            )

            # Now parse it. If it does not work, query gpt-3.5 again to clean it in
            # the right format.
            potential_personas = [{"persona": "test", "description": "test"}]

            potential_personas = (
                options.personas if options.personas else []
            ) + frontend_generator.parse_potential_personas(potential_personas_str)[
                "results"
            ]

            cache.set(cache_key, potential_personas)

            return render_frontend_template(
                potential_personas, frontend_endpoint, request
            )

        async def handle_form(request: Request, persona: Annotated[str, Form()]):
            scheme = request.url.scheme
            server_host = request.headers.get("host")
            full_url = f"{scheme}://{server_host}"

            logging.info(f"Generating frontend for url: {full_url}")

            return generate_frontend(persona, full_url)

        app.add_api_route(
            f"/{frontend_endpoint}",
            fast_api_frontend,
            methods=["GET"],
            response_class=HTMLResponse,
        )
        app.add_api_route(
            f"/gen_{frontend_endpoint}",
            handle_form,
            methods=["POST"],
            response_class=HTMLResponse,
        )

    elif framework_name == FLASK:

        def handle_form():
            persona = request.form.get("persona")

            logging.info(f"Generating frontend for url: {request.url}")

            return generate_frontend(persona, request.url)

        app.add_url_rule(f"/{frontend_endpoint}", "frontend", frontend, methods=["GET"])
        app.add_url_rule(
            f"/gen_{frontend_endpoint}", "handle_form", handle_form, methods=["POST"]
        )

    return app
