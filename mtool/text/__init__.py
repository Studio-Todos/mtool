"""
Text processing tools for mtool
"""

import click
from mtool.text.process import process_group


@click.group(name="text")
def text_group():
    """
    Text processing and analysis tools.
    
    Count lines, words, characters, and bytes. Search and replace text with regex
    support. Sort, deduplicate, and analyze text files. Generate text statistics
    and word frequency analysis.
    """
    pass


# Register text tools
text_group.add_command(process_group) 