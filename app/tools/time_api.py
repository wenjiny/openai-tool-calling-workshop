# app/tools/time_api.py
import requests

GET_TIME_SCHEMA = {
    "name": "get_time",
    "description": "Return the current date/time for an IANA timezone via worldtimeapi.org.",
    "parameters": {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "IANA timezone, e.g. 'Europe/Stockholm' or 'America/New_York'."
            }
        },
        "required": ["timezone"],
        "additionalProperties": False
    },
    "strict": True,
}

def get_time(timezone: str) -> dict:
    tz = (timezone or "").strip()
    try:
        resp = requests.get(f"https://worldtimeapi.org/api/timezone/{tz}", timeout=10)
        if resp.status_code != 200:
            return {"ok": False, "timezone": tz, "error": f"HTTP {resp.status_code}"}
        data = resp.json()
        # Extract a few stable fields
        return {
            "ok": True,
            "timezone": tz,
            "datetime": data.get("datetime"),
            "utc_offset": data.get("utc_offset"),
            "day_of_week": data.get("day_of_week"),
        }
    except Exception as e:
        return {"ok": False, "timezone": tz, "error": str(e)}
