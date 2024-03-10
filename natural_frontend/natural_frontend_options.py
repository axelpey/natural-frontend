# Define the Options type, colors needs to be a dict with keys "primary" and "secondary"
# And personas needs to be a list of dicts with keys "persona" and "description"
from typing import Dict, List, Optional


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