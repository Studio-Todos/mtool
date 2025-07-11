"""
Convert operations for mtool
"""

import click
from mtool.convert.file import file_convert_group
from mtool.convert.pdf import pdf_convert_group
from mtool.convert.data import data_convert_group


@click.group(name="convert")
def convert_group():
    """
    File and data format conversion tools.
    
    Convert images, audio, and video files between formats. Transform PDFs to/from
    images and extract text. Convert between CSV, JSON, and other data formats
    with formatting and validation options.
    """
    pass


# Register convert tools
convert_group.add_command(file_convert_group)
convert_group.add_command(pdf_convert_group)
convert_group.add_command(data_convert_group) 