"""
Web utility tools for mtool
"""

import click
from mtool.web.url import url_group
from mtool.web.status import status_group
from mtool.web.download import download_group


@click.group(name="web")
def web_group():
    """
    Web utilities and network operations.
    
    URL manipulation (shorten, expand, encode/decode, validation), website status
    monitoring (ping, port checking, SSL certificates), and file download utilities
    with progress tracking and resume capabilities.
    """
    pass


# Register web tools
web_group.add_command(url_group)
web_group.add_command(status_group)
web_group.add_command(download_group) 