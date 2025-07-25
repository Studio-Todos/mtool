#!/usr/bin/env python3
"""
Main CLI entry point for mtool
"""

import click
import sys
from pathlib import Path

# Import tool categories
from mtool.file import file_group
from mtool.util import util_group
from mtool.pdf import pdf_group
from mtool.web import web_group
from mtool.text import text_group
from mtool.convert import convert_group
from mtool.image.process import image_group
from mtool.video import video_group
from mtool.tetris import tetris_group
from mtool.ln import ln_group


@click.group()
@click.version_option(version="0.1.0", prog_name="mtool")
def main():
    """
    mtool - A comprehensive modular CLI tool for file operations, data conversion, 
    web utilities, text processing, and system utilities.
    
    Use 'mtool <category> <tool> --help' for specific tool help.
    """
    pass


# Register tool categories
main.add_command(file_group)
main.add_command(util_group)
main.add_command(pdf_group)
main.add_command(web_group)
main.add_command(text_group)

main.add_command(convert_group)
main.add_command(image_group)
main.add_command(video_group)
main.add_command(tetris_group)
main.add_command(ln_group)


if __name__ == "__main__":
    main() 