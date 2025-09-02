# app/tools/currency.py
from typing import Dict

# Mock FX table so the workshop runs without external APIs
# Rates are illustrative, not real-time
_FAKE_RATES: Dict[str, Dict[str, float]] = {
    "SEK": {"EUR": 0.09, "USD": 0.10, "SEK": 1.0},
    "EUR": {"SEK": 11.1,  "USD": 1.08, "EUR": 1.0},
    "USD": {"SEK": 10.2,  "EUR": 0.92, "USD": 1.0},
}

GET_CURRENCY_RATE_SCHEMA = {
    "name": "get_currency_rate",
    "description": "Return a mock FX rate from base to quote (no external API).",
    "parameters": {
        "type": "object",
        "properties": {
            "base": {"type": "string", "description": "3-letter base currency (e.g., SEK)."},
            "quote": {"type": "string", "description": "3-letter quote currency (e.g., EUR)."},
        },
        "required": ["base", "quote"],
        "additionalProperties": False
    },
    "strict": True,
}

def get_currency_rate(base: str, quote: str) -> dict:
    b = (base or "").upper().strip()
    q = (quote or "").upper().strip()
    if b not in _FAKE_RATES:
        return {"ok": False, "message": f"Unknown base currency '{base}'"}
    rate = _FAKE_RATES[b].get(q)
    if rate is None:
        return {"ok": False, "message": f"No rate for {b}->{q}"}
    return {"ok": True, "base": b, "quote": q, "rate": rate}
