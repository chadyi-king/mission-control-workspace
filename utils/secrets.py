import os


def get_secret(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise KeyError(f"Missing secret: {name}")
