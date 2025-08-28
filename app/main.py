import os
import typer
from rich import print
from dotenv import load_dotenv
from .runner_responses import run_once as run_responses
from .runner_chat import run_once as run_chat

app = typer.Typer(help="OpenAI function/tool-calling workshop runner")

@app.command()
def chat(prompt: str, model: str = "gpt-4o-mini"):
    """Classic Chat Completions + tools."""
    run_chat(prompt, model)

@app.command()
def responses(prompt: str, model: str = "gpt-4.1-mini"):
    """Modern Responses API + tools (recommended)."""
    run_responses(prompt, model)

if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[red]Missing OPENAI_API_KEY. Create a .env from .env.example[/red]")
    app() 
