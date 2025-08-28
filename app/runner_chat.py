import json
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from .tools import TOOL_SPECS_CHAT, FUNCTIONS

console = Console()

def run_once(prompt: str, model: str = "gpt-4o-mini") -> None:
    load_dotenv()
    client = OpenAI() 

    messages = [{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}]

    
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOL_SPECS_CHAT,        # <-- keep nested format for Chat API
        tool_choice="auto",
    )

    msg = resp.choices[0].message
    if msg.tool_calls:
        # Execute tool(s)
        tool_messages = []
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            console.print(f"[yellow]→ Tool call[/yellow] [bold]{name}[/bold] args={args}")
            fn = FUNCTIONS.get(name)
            if not fn:
                result = {"ok": False, "error": f"Unknown tool: {name}"}
            else:
                try:
                    result = fn(**args)
                except Exception as e:
                    result = {"ok": False, "error": f"{e!r}"}

            tool_messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": name,
                "content": json.dumps(result, ensure_ascii=False),
            })

        # Ask the model to incorporate tool results
        messages.extend([msg])          # assistant "tool_calls"
        messages.extend(tool_messages)  # tool outputs

        resp2 = client.chat.completions.create(
            model=model,
            messages=messages
        )
        console.print(f"[bold cyan]Assistant:[/bold cyan] {resp2.choices[0].message.content}")
    else:
        console.print(f"[bold cyan]Assistant:[/bold cyan] {msg.content}")
