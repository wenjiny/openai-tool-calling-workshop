# Function Calling Workshop (Responses API Only)

This hands-on workshop walks you through the **OpenAI Responses API + function (tool) calling**. You’ll learn how to wire up Python functions as tools, how the model calls them with validated JSON, and how to optionally force the assistant’s **final answer** to be **Structured Output** (strict JSON), perfect for automation.

## What we’ll do

1. **Call a basic function with mock data** (so you can see the model actually invoking your code).
2. **Call the same kind of function with/without Structured Output** (human text vs strict JSON).
3. **Call a function that uses a real HTTP API**, again with/without Structured Output.
4. (Optional) **Write your own function** and add it to the tool space (mock or real API).

---

# Get started

1. **Activate your virtualenv**

* macOS/Linux:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```
* Windows (PowerShell):

  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate
  ```

2. **Install deps**

```bash
pip install -r requirements.txt
```

3. **Set your API key**
   Create a `.env` file:

```
OPENAI_API_KEY=sk-...
```

4. **Run**

```bash
python -m app.main run "What's the weather in Stockholm in celsius?"
```

> Tip: You can persist a conversation across runs with `--session=NAME`.
> You can turn on Structured Output with `--structured=currency` or `--structured=time`.

---

# Folder structure

```
.venv/
app/
├─ main.py                # CLI entrypoint (Typer). Adds --session and --structured flags.
├─ runner_responses.py    # Orchestrates the Responses API + function calling handshake.
├─ session_store.py       # Simple JSON disk store for multi-turn sessions across CLI runs.
└─ tools/
   ├─ __init__.py         # Tool registry: tool schemas for Responses + dispatcher (name → function).
   ├─ weather.py          # Tool 1: get_weather (mock DB). Good for a quick, offline demo.
   ├─ currency.py         # Tool 2: get_currency_rate (mock FX DB). Shows a 2nd mock tool.
   └─ time_api.py         # Tool 3: get_time (real HTTP API via worldtimeapi.org).
└─ schemas/
   ├─ currency_answer.json # Structured Output schema for the final assistant answer to FX questions.
   └─ time_answer.json     # Structured Output schema for the final assistant answer to time questions.
.env
.gitignore
README.md
requirements.txt
```

---

# How the function calling API works (Responses)

1. You send your **prompt** + your **tool schemas** to the **Responses API**.
2. The model may return one or more **`function_call`** items with `name`, `call_id`, and `arguments`.
3. Your runner:

   * **Executes** the Python function by **name** (using a dispatcher dict).
   * **Appends two inputs** to the conversation:

     * the **echo** of the `function_call`
     * the **`function_call_output`** with your tool’s JSON result (same `call_id`)
4. You call the **Responses API again**. Now the model has the tool outputs and can synthesize the **final answer**.

**Key benefit:** the model never runs your code directly; it asks you to run a tool with specific, schema-validated arguments.

---

# Structured Output vs Freeform

* **Freeform (default)**
  The **final assistant message** is normal text for humans. Your **tool outputs are still JSON** (because you return dicts from Python), but the *assistant’s* last message is prose.

* **Structured Output**
  You ask the model to make the **final assistant message** a **strict JSON** object that **validates** against a schema you provide (e.g., `schemas/currency_answer.json`).
  Great for downstream parsing, dashboards, and automation.

> Note: Structured Output affects the **final assistant reply**, not your tool return values.

---

# Session store — how it works

* We keep conversation history on disk in `./.sessions/<name>.json`.
* When you run with `--session=demo`:

  * If **no file exists**, we start empty and **create** it after the run.
  * If it **exists**, we **load** the prior messages, append your new turn(s), and **save** the updated conversation.
* This lets you continue a chat across separate CLI invocations.

Usage examples:

```bash
# Starts a new session called 'demo' (creates file on first run)
python -m app.main run "Hello!" --session=demo

# Continues the same conversation later
python -m app.main run "Follow-up using context..." --session=demo
```

To reset, delete `.sessions/demo.json`.

---

# File-by-file

### `app/main.py`

* Typer CLI entrypoint.
* Command: `run`

  * `prompt` (positional)
  * `--session / -s` (optional): persist conversation
  * `--structured / -f` (optional): choose `currency` or `time` Structured Output schema
* Calls `runner_responses.run_once(...)`.

### `app/runner_responses.py`

* Implements the **Responses** handshake:

  * First call to `responses.create(...)` with `tools=...`
  * If the model produces `function_call` items:

    * run the Python function
    * append `function_call` (echo) **and** `function_call_output` (your JSON)
  * Second call to `responses.create(...)` to synthesize the **final answer**
* Applies **Structured Output** when `--structured` is set (loads schema JSON from `app/schemas/`).
* Prints assistant text and simple tool-call logs (name, args, call\_id).

### `app/session_store.py`

* Tiny helper to **load/save** a list of messages (JSON) by session name:

  * `load_session(name) → list`
  * `save_session(name, messages) → None`
* Stores files under `./.sessions/`.

### `app/tools/__init__.py`

* Central **tool registry** for the Responses API:

  * `TOOL_SPECS_RESPONSES`: flattened schemas (Responses expects `{type:"function", name, parameters, ...}`).
  * `FUNCTIONS`: dispatcher dict mapping tool name → Python function.

### `app/tools/weather.py`

* `get_weather(city, unit)` returns mock temps from a tiny in-memory DB.
* `GET_WEATHER_SCHEMA`: JSON Schema describing args (`city`, `unit`), `strict: true`.

### `app/tools/currency.py`

* `get_currency_rate(base, quote)` returns mock FX rates.
* `GET_CURRENCY_RATE_SCHEMA`: JSON Schema for `base` and `quote`.

### `app/tools/time_api.py`

* `get_time(timezone)` queries the **WorldTimeAPI** (real HTTP).
* `GET_TIME_SCHEMA`: JSON Schema for `timezone`.
* Requires `requests` in `requirements.txt`.

### `app/schemas/*.json`

* **currency\_answer.json** / **time\_answer.json** define a **Structured Output** schema for the **final assistant message** when answering currency/time questions.
* Flip on with `--structured=currency` or `--structured=time`.

---

# Try it — Commands

> You can add `--session=NAME` to any of these to keep the conversation history.

### 1) Mock weather (freeform)

```bash
python -m app.main run "What's the weather in Stockholm in celsius?"
```

### 2) Mock currency — freeform vs Structured Output

* **Freeform**

  ```bash
  python -m app.main run "What's the mock FX rate from SEK to EUR? Please call get_currency_rate."
  ```
* **Structured Output**

  ```bash
  python -m app.main run "What's the mock FX rate from SEK to EUR? Please call get_currency_rate." --structured=currency
  ```

### 3) Real API time — freeform vs Structured Output

* **Freeform**

  ```bash
  python -m app.main run "What is the current time in Europe/Stockholm? Please call get_time."
  ```
* **Structured Output**

  ```bash
  python -m app.main run "What is the current time in Europe/Stockholm? Please call get_time." --structured=time
  ```

---

# Add your own function (tool)

You’ll do three things:

## A) Create the tool (mock or real API)

**Example: mock** — `app/tools/hello.py`

```python
GET_HELLO_SCHEMA = {
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
    return {"ok": True, "message": f"Hello, {name}!"}
```

**Example: real API** — `app/tools/ip_api.py`

```python
import requests

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
        return {"ok": False, "error": str(e)}
```

> For real APIs, add any deps to `requirements.txt` (e.g., `requests`).

## B) Register the tool

Update `app/tools/__init__.py`:

```python
from .hello import GET_HELLO_SCHEMA, say_hello
from .ip_api import GET_IP_GEO_SCHEMA, get_ip_geo

TOOL_SPECS_RESPONSES += [
    {"type": "function", **GET_HELLO_SCHEMA},
    {"type": "function", **GET_IP_GEO_SCHEMA},
]

FUNCTIONS.update({
    "say_hello": say_hello,
    "get_ip_geo": get_ip_geo,
})
```

## C) (Optional) Add Structured Output schema

Create `app/schemas/hello_answer.json`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "HelloAnswer",
    "schema": {
      "type": "object",
      "properties": {
        "ok": { "type": "boolean" },
        "message": { "type": "string" }
      },
      "required": ["ok", "message"]
    },
    "strict": true
  }
}
```

Add a mapping entry in `runner_responses.py` if you want to trigger it via CLI:

```python
SCHEMA_MAP["hello"] = SCHEMAS_DIR / "hello_answer.json"
```

Then:

```bash
python -m app.main run "Please call say_hello with name='Wenjin'." --structured=hello
```

---

# When to use Function Calling vs Agent frameworks

There are higher-level **agent** frameworks, e.g., **Google’s Agent Development Kit (ADK)** and **OpenAI’s Agents SDK**. Function calling is the **low-level primitive**; agent SDKs add orchestration, multi-agent composition, guardrails, and observability.

| Dimension      | Function Calling (Responses API)                              | OpenAI Agents SDK                                                             | Google ADK                                                            |
| -------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Primary role   | Single agent + tools; schema-validated tool calls             | Higher-level orchestration on top of Responses; handoffs, guardrails, tracing | Multi-agent framework; coordinator + specialists; routing, evaluation |
| Orchestration  | You write the loop (detect `function_call`, run, echo/output) | Built-ins for multi-step flows, handoffs, guardrails                          | Built-ins for multi-agent composition, routing, parallel tasks        |
| Concurrency    | Manual (you can do it, but you manage it)                     | Patterns for parallel steps and handoffs                                      | First-class parallelism for subtasks                                  |
| Review/QA      | DIY (validators, retries, structured outputs)                 | Reviewer/guardrail patterns + observability                                   | Reviewer/feedback loops + evaluation tooling                          |
| Best when      | Simple apps, one agent with a handful of tools                | You need multi-step flows, safety gates, tracing                              | You want a model-agnostic multi-agent system similar to MAS research  |
| Migration path | Start here (minimal surface)                                  | Add when complexity grows                                                     | Use when you want MAS patterns and Google’s ecosystem                 |

**Rule of thumb**

* One capable assistant + a few tools, mostly sequential → **Function calling** is perfect.
* Multiple roles, parallel subtasks, compliance/review gates, traceability → **Agents SDK / ADK**.

> If you want to check out **Google’s Agent Development Kit**, you can explore the **AI Academy area in the B2 office area**.

---

# Troubleshooting

* **“Unexpected extra argument …”**
  Use the `run` subcommand:

  ```bash
  python -m app.main run "Your prompt here"
  ```
* **Model didn’t call my tool**
  Nudge it in the prompt: *“Please call `get_time`.”*
* **Real API failures**
  Tools return `{"ok": False, "error": "..."}`; the assistant will explain the issue.
* **No persistent context**
  Add `--session=NAME` to keep history across runs.

---

Happy building! 🎉
