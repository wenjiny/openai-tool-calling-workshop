from typing import Literal, TypedDict, Dict

# Minimal mock DB so workshop runs without external APIs
_FAKE_WEATHER: Dict[str, Dict[str, float]] = {
    "stockholm": {"c": 18.0, "f": 64.4},
    "gothenburg": {"c": 17.0, "f": 62.6},
    "malmo": {"c": 19.0, "f": 66.2},
}

class GetWeatherArgs(TypedDict):
    city: str
    unit: Literal["c", "f"]

# JSON Schema for tool definition
GET_WEATHER_SCHEMA = {
    "name": "get_weather",
    "description": "Return the current temperature for a city (mock data).",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name."},
            "unit": {
                "type": "string",
                "enum": ["c", "f"],
                "description": "c for Celsius, f for Fahrenheit",
                "default": "c"  # optional; model typically fills it anyway
            }
        },
        # <-- strict requires 'required' to include *all* keys in properties
        "required": ["city", "unit"],
        "additionalProperties": False
    },
    "strict": True,
}


def get_weather(city: str, unit: str = "c") -> dict:
    c = city.strip().lower()
    d = _FAKE_WEATHER.get(c)
    if not d:
        return {"ok": False, "message": f"No data for '{city}'"}
    temp = d.get(unit, d["c"])
    return {"ok": True, "city": city, "unit": unit, "temperature": temp}
