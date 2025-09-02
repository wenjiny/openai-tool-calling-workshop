# app/runner_responses.py
import json
from pathlib import Path
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console

from .tools import TOOL_SPECS_RESPONSES, FUNCTIONS

# Optional session persistence (if you created session_store.py)
try:
    from .session_store import load_session, save_session
    HAS_SESSIONS = True
except Exception:
    HAS_SESSIONS = False

console = Console()

SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"
SCHEMA_MAP = {
    "currency": SCHEMAS_DIR / "currency_answer.json",
    "time": SCHEMAS_DIR / "time_answer.json",
    #"hello": SCHEMAS_DIR / "hello_answer.json",
}

def _load_text_format(kind: Optional[str]) -> Optional[dict]:
    """
    kind: None | 'currency' | 'time'
    Returns a dict suitable for Responses 'text': {'format': <dict>}
    """
    if not kind:
        return None
    p = SCHEMA_MAP.get(kind.lower())
    if not p or not p.exists():
        console.print(f"[red]Structured format '{kind}' not found at {p}[/red]")
        return None
    try:
        fmt = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]Failed to load schema {p}: {e!r}[/red]")
        return None

    # Expect the direct 'text.format' object shape:
    # { "type": "json_schema", "name": "...", "schema": {...}, "strict": true }
    if fmt.get("type") != "json_schema" or "schema" not in fmt:
        console.print(f"[red]Invalid schema object in {p} "
                      f"(expected keys: type='json_schema' and 'schema').[/red]")
        return None
    return fmt


def run_once(
    prompt: str,
    model: str = "gpt-4o-mini",
    session: Optional[str] = None,
    structured: Optional[str] = None,  # 'currency' | 'time' | None
) -> None:
    load_dotenv()
    client = OpenAI()

    # Load prior conversation if sessions are enabled
    if session and HAS_SESSIONS:
        input_messages = load_session(session)
    else:
        input_messages = []

    # 1) Start with user message
    input_messages.append({"role": "user", "content": prompt})

    # Load 'text.format' if requested
    text_format_obj = _load_text_format(structured)
    text_arg = {"format": text_format_obj} if text_format_obj else None

    # First pass: let the model decide whether to call tools
    first_args = dict(
        model=model,
        input=input_messages,
        tools=TOOL_SPECS_RESPONSES,
        tool_choice="auto",
        parallel_tool_calls=False,  # linear for the workshop
    )
    if text_arg:
        first_args["text"] = text_arg

    resp = client.responses.create(**first_args)

    # If the model already answered, print it and persist (if sessions)
    if getattr(resp, "output_text", None):
        console.print(f"[bold cyan]Assistant:[/bold cyan] {resp.output_text}")
        if session and HAS_SESSIONS:
            input_messages.append({"role": "assistant", "content": resp.output_text})

    # 2) Execute any tool calls and append BOTH the call and its output
    had_tools = False
    for item in (resp.output or []):
        if getattr(item, "type", "") == "function_call":
            had_tools = True
            name = getattr(item, "name", None)
            call_id = getattr(item, "call_id", None)
            args_raw = getattr(item, "arguments", "{}")
            try:
                args = json.loads(args_raw) if isinstance(args_raw, str) else (args_raw or {})
            except Exception:
                args = {}

            console.print(
                f"[yellow]→ Tool call[/yellow] [bold]{name}[/bold] "
                f"[dim]id={call_id}[/dim] args={args}"
            )

            fn = FUNCTIONS.get(name)
            if not fn:
                result = {"ok": False, "error": f"Unknown tool: {name}"}
            else:
                try:
                    result = fn(**args)
                except Exception as e:
                    result = {"ok": False, "error": f"{e!r}"}

            # Echo the function call back to the model
            input_messages.append({
                "type": "function_call",
                "name": name,
                "call_id": call_id,
                "arguments": json.dumps(args, ensure_ascii=False)
            })
            console.print(f"[green]✔ Echoed function_call[/green] id={call_id}")

            # Attach the tool result tied to the same call_id
            input_messages.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result, ensure_ascii=False)
            })
            console.print(f"[green]✔ Attached function_call_output[/green] id={call_id}")

    # 3) Ask the model to produce the final answer with the tool outputs in context
    if had_tools:
        second_args = dict(
            model=model,
            input=input_messages,
            tools=TOOL_SPECS_RESPONSES,
            tool_choice="auto",
            parallel_tool_calls=False,
        )
        if text_arg:
            second_args["text"] = text_arg

        resp2 = client.responses.create(**second_args)

        if getattr(resp2, "output_text", None):
            console.print(f"[bold cyan]Assistant:[/bold cyan] {resp2.output_text}")
            if session and HAS_SESSIONS:
                input_messages.append({"role": "assistant", "content": resp2.output_text})

    # Save session (if enabled)
    if session and HAS_SESSIONS:
        save_session(session, input_messages)
