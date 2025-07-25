import argparse
from rich.console import Console
from rich.panel import Panel
from openai import OpenAI
import os
import pyperclip

def spice_up_text(text):
    """
    Spice up the given text using an AI model.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://github.com/search?q=repo%3AInfiniThink-Dev%2Fmtool",
            "X-Title": "mtool",
        },
        model="qwen/qwen3-235b-a22b-2507:free",
        messages=[
            {
                "role": "system",
                "content": "You are a professional LinkedIn writer. Given a brief summary of technical work, generate a 1-3 sentence LinkedIn post that:\n- Highlights the value of the work\n- Is easy to read\n- Sounds confident but not arrogant\n- Can include 1–2 emojis or light hashtags"
            },
            {
                "role": "user",
                "content": f"Summary: \"{text}\""
            }
        ]
    )
    return completion.choices[0].message.content

def main():
    """
    The main function for the spiceup tool.
    """
    parser = argparse.ArgumentParser(description="Spice up your summaries into polished LinkedIn posts.")
    parser.add_argument("summary", nargs="?", help="The summary to spice up.")
    args = parser.parse_args()

    console = Console()

    if args.summary:
        spiced_text = spice_up_text(args.summary)
        pyperclip.copy(spiced_text)
        console.print(Panel(spiced_text, title="Polished LinkedIn Post (Copied to Clipboard!)", border_style="green"))
    else:
        console.print("Paste your summary:")
        summary = input("> ")
        spiced_text = spice_up_text(summary)
        pyperclip.copy(spiced_text)
        console.print(Panel(spiced_text, title="Polished LinkedIn Post (Copied to Clipboard!)", border_style="green"))

if __name__ == "__main__":
    main()
