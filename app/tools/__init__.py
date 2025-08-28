from .weather import GET_WEATHER_SCHEMA, get_weather

# Chat Completions format → nested under "function"
TOOL_SPECS_CHAT = [
    {"type": "function", "function": GET_WEATHER_SCHEMA},
]

# Responses API format → flattened (name/parameters at top level)
TOOL_SPECS_RESPONSES = [
    {"type": "function", **GET_WEATHER_SCHEMA},  # expands: name, description, parameters, strict
]

# Dispatcher
FUNCTIONS = {
    "get_weather": get_weather,
}
