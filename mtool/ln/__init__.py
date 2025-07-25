import click
from mtool.ln.post import main as post_main

@click.group("ln")
def ln_group():
    """LinkedIn tools."""
    pass

@ln_group.command("post")
@click.argument("summary", nargs=-1)
def post(summary):
    """Spice up your summaries into polished LinkedIn posts."""
    # Reconstruct the summary string
    summary_str = " ".join(summary)

    import sys
    # Backup original argv
    original_argv = sys.argv
    # Set argv for the post_main function
    sys.argv = ["", summary_str] if summary_str else [""]

    try:
        post_main()
    finally:
        # Restore original argv
        sys.argv = original_argv

def main():
    ln_group()

if __name__ == "__main__":
    main()
