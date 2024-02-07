from collections.abc import Callable
import inspect
from typing import Any


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


# TODO: Make route a Struct with just a "code" member to be framework-agnostic
def aggregate_all_api_routes(routes: list[Any], exclude_route: Callable[[Any], bool]):
    concat_sources = []
    for route in routes:
        if not exclude_route(route):
            concat_sources.append(inspect.getsource(route.endpoint))

    concat_sources = "\n\n".join(concat_sources)

    return concat_sources
