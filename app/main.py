import os
import typer
from rich import print
from dotenv import load_dotenv
from .runner_responses import run_once as run_responses

app = typer.Typer(help="OpenAI function/tool-calling workshop (Responses API only)")

@app.command(name="run")
def run(prompt: str, model: str = "gpt-4.1-mini"):
    """Run the workshop using the modern Responses API + tools."""
    run_responses(prompt, model)

if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[red]Missing OPENAI_API_KEY. Create a .env from .env.example[/red]")
    app()
