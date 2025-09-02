"""import requests

GET_IP_GEO_SCHEMA = {
    "name": "get_ip_geo",
    "description": "Lookup IP geolocation via ipapi.co (public demo).",
    "parameters": {
        "type": "object",
        "properties": {
            "ip": {"type": "string", "description": "IPv4 or IPv6 address"}
        },
        "required": ["ip"],
        "additionalProperties": False
    },
    "strict": True,
}

def get_ip_geo(ip: str) -> dict:
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code}"}
        data = r.json()
        return {
            "ok": True,
            "ip": ip,
            "country": data.get("country_name"),
            "city": data.get("city"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}"""