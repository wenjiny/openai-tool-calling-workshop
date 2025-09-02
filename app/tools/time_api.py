# app/tools/time_api.py
import requests

GET_TIME_SCHEMA = {
    "name": "get_time",
    "description": "Return the current date/time for an IANA timezone via timeapi.io.",
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
    """
    Calls timeapi.io to fetch the current local time for an IANA time zone.
    Example: https://www.timeapi.io/api/Time/current/zone?timeZone=Europe/Stockholm
    Returns a compact JSON your model can use.
    """
    tz = (timezone or "").strip()
    if not tz:
        return {"ok": False, "timezone": tz, "error": "Empty timezone"}

    url = "https://www.timeapi.io/api/Time/current/zone"
    try:
        r = requests.get(url, params={"timeZone": tz}, timeout=10)
    except Exception as e:
        return {"ok": False, "timezone": tz, "error": f"Network error: {e}"}

    if r.status_code != 200:
        # Try to include a small hint from the body if present
        body = ""
        try:
            body = r.text[:200]
        except Exception:
            pass
        return {
            "ok": False,
            "timezone": tz,
            "error": f"HTTP {r.status_code}",
            "hint": body,
        }

    try:
        data = r.json()
    except Exception as e:
        return {"ok": False, "timezone": tz, "error": f"Invalid JSON: {e}"}

    # timeapi.io fields commonly include:
    # year, month, day, hour, minute, seconds, milliSeconds,
    # dateTime (ISO-8601), date, time, timeZone, dayOfWeek, dstActive
    return {
        "ok": True,
        "timezone": data.get("timeZone") or tz,
        "datetime": data.get("dateTime"),
        "day_of_week": data.get("dayOfWeek"),
        "dst_active": data.get("dstActive"),
        # Keep extras in case you want them later:
        "raw": {
            "year": data.get("year"),
            "month": data.get("month"),
            "day": data.get("day"),
            "hour": data.get("hour"),
            "minute": data.get("minute"),
            "seconds": data.get("seconds"),
            "milliSeconds": data.get("milliSeconds"),
        },
    }
