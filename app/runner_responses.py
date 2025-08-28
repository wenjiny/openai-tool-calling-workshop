import json
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from .tools import TOOL_SPECS_RESPONSES, FUNCTIONS

console = Console()

def run_once(prompt: str, model: str = "gpt-4.1-mini") -> None:
    load_dotenv()
    client = OpenAI()

    # 1) Start the conversation with a normal user message
    input_messages = [{"role": "user", "content": prompt}]

    resp = client.responses.create(
        model=model,
        input=input_messages,
        tools=TOOL_SPECS_RESPONSES,
        tool_choice="auto",
        parallel_tool_calls=False,  # keep it simple for the workshop
    )

    # If the model already answered, print it
    if getattr(resp, "output_text", None):
        console.print(f"[bold cyan]Assistant:[/bold cyan] {resp.output_text}")

    # 2) Execute any tool calls and append BOTH the call and its output as new inputs
    had_tools = False
    for item in resp.output or []:
        if getattr(item, "type", "") == "function_call":
            had_tools = True
            name = getattr(item, "name", None)
            call_id = getattr(item, "call_id", None)
            args_raw = getattr(item, "arguments", "{}")
            try:
                args = json.loads(args_raw) if isinstance(args_raw, str) else (args_raw or {})
            except Exception:
                args = {}

            console.print(f"[yellow]→ Tool call[/yellow] [bold]{name}[/bold] args={args}")

            fn = FUNCTIONS.get(name)
            if not fn:
                result = {"ok": False, "error": f"Unknown tool: {name}"}
            else:
                try:
                    result = fn(**args)
                except Exception as e:
                    result = {"ok": False, "error": f"{e!r}"}

            # Append the function_call the model made (echo it back)
            input_messages.append({
                "type": "function_call",
                "name": name,
                "call_id": call_id,
                "arguments": json.dumps(args, ensure_ascii=False)
            })
            # Append your tool result tied to the same call_id
            input_messages.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result, ensure_ascii=False)
            })

    # 3) Ask the model to produce the final answer with the tool outputs in context
    if had_tools:
        resp2 = client.responses.create(
            model=model,
            input=input_messages,
            tools=TOOL_SPECS_RESPONSES,
            tool_choice="auto",
            parallel_tool_calls=False,
        )
        if getattr(resp2, "output_text", None):
            console.print(f"[bold cyan]Assistant:[/bold cyan] {resp2.output_text}") 
