from .weather import GET_WEATHER_SCHEMA, get_weather
from .currency import GET_CURRENCY_RATE_SCHEMA, get_currency_rate   # NEW
from .time_api import GET_TIME_SCHEMA, get_time                     # NEW

TOOL_SPECS_RESPONSES = [
    {"type": "function", **GET_WEATHER_SCHEMA},
    {"type": "function", **GET_CURRENCY_RATE_SCHEMA},  # NEW
    {"type": "function", **GET_TIME_SCHEMA},           # NEW
]

FUNCTIONS = {
    "get_weather": get_weather,
    "get_currency_rate": get_currency_rate,  # NEW
    "get_time": get_time,                    # NEW
}
