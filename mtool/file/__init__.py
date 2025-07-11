"""
File operation tools for mtool
"""

import click
from mtool.file.compress import compress_group
from mtool.file.extract import extract_group
from mtool.file.manage import manage_group


@click.group(name="file")
def file_group():
    """
    File compression and extraction operations.
    
    Compress files and directories into various archive formats (ZIP, TAR, GZIP, BZIP2, XZ).
    Extract compressed archives with automatic format detection.
    """
    pass


# Register file tools
file_group.add_command(compress_group)
file_group.add_command(extract_group)
file_group.add_command(manage_group) 