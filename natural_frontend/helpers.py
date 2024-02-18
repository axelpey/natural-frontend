from collections.abc import Callable
import inspect
from typing import Any

from .constants import FAST_API, FAST_API_ROUTE_TYPE, BAD_ROUTES_BY_FRAMEWORK

class Route:
    def __init__(self, code: str):
        self.code = code


def create_api_short_documentation_prompt(routes_code: str):
    return [
        {
            "role": "system",
            "content": "Write a short documentation for each route. What it does, "
            + "what it takes as input, what it returns.",
        },
        {
            "role": "user",
            "content": routes_code,
        },
    ]


def aggregate_all_api_routes(app: Any, framework_name: str):
    if framework_name == FAST_API:
        routes = app.routes
    else:
        raise ValueError("Framework not supported")
    
    concat_sources = []
    for route in routes:
        clean_route = convert_and_filter_route_by_framework(route, framework_name)
        if clean_route is not None:
            concat_sources.append(inspect.getsource(clean_route.code))

    concat_sources = "\n\n".join(concat_sources)

    return concat_sources

def convert_and_filter_route_by_framework(route: Any, framework_name: str) -> Route:
    if framework_name == FAST_API:
        if not route.__class__.__name__ == FAST_API_ROUTE_TYPE or route.endpoint.__name__ in BAD_ROUTES_BY_FRAMEWORK[framework_name]:
            return None
        return Route(route.endpoint)
    else:
        raise ValueError("Framework not supported")

def get_framework_name_or_crash(app: Any) -> str :
    if app.__class__.__name__ == FAST_API:
        return FAST_API
    else:
        raise ValueError("Framework not supported")
    