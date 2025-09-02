import os
import typer
from typing import Optional
from rich import print
from dotenv import load_dotenv
from .runner_responses import run_once as run_responses

app = typer.Typer(help="OpenAI function/tool-calling workshop (Responses API only)")

@app.command(name="run")
def run(
    prompt: str,
    model: str = typer.Option("gpt-4o-mini", help="Responses model to use."),
    session: Optional[str] = typer.Option(
        None, "--session", "-s", help="Session name to persist conversation history."
    ),
    structured: Optional[str] = typer.Option(
        None,
        "--structured",
        "-f",
        help="Structured output format: 'currency' or 'time' (default: none).",
    ),
):
    """Run the workshop using the modern Responses API + tools."""
    run_responses(prompt, model, session=session, structured=structured)

if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[red]Missing OPENAI_API_KEY. Create a .env from .env.example[/red]")
    app()
