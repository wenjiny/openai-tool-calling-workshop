"""GET_HELLO_SCHEMA = {
    "name": "say_hello",
    "description": "Return a friendly greeting.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Person's name"}
        },
        "required": ["name"],
        "additionalProperties": False
    },
    "strict": True,
}

def say_hello(name: str) -> dict:
    return {"ok": True, "message": f"Hello, {name}!"}"""