from collections.abc import Callable
import inspect
from typing import Any


def create_seed_prompt(
    framework_name: str,
    language_to_inject: str,
    result_variable_name: str,
    helper_to_call_routes_name: str,
):
    return [
        {
            "role": "system",
            "content": f"You will be given a {framework_name} codebase and a human-language query. "
            + f"Write the {language_to_inject} function that executes the query and stores the result in the global variable {result_variable_name}. "
            + f"You can call the routes with {helper_to_call_routes_name}(route_name, params). Don't import any module. GIVE ME ONLY CODE, NOTHING ELSE.",
        }
    ]


# TODO: Make route a Struct with just a "code" member to be framework-agnostic
def aggregate_all_api_routes(routes: list[Any], exclude_route: Callable[[Any], bool]):
    concat_sources = []
    for route in routes:
        if not exclude_route(route):
            concat_sources.append(inspect.getsource(route.endpoint))

    concat_sources = "\n\n".join(concat_sources)

    return concat_sources
