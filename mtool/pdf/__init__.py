"""
PDF operation tools for mtool
"""

import click
from mtool.pdf.info import info_group
from mtool.pdf.split import split_group
from mtool.pdf.merge import merge_group
from mtool.pdf.compress import compress_group


@click.group(name="pdf")
def pdf_group():
    """
    PDF document operations and manipulation.
    
    Get PDF information (pages, size, metadata), split PDFs by pages or ranges,
    merge multiple PDFs into single documents, and compress PDF files to reduce size.
    """
    pass


# Register PDF tools
pdf_group.add_command(info_group)
pdf_group.add_command(split_group)
pdf_group.add_command(merge_group)
pdf_group.add_command(compress_group) 