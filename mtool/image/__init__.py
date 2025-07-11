"""
Image processing tools for mtool
"""

import click
from mtool.image.process import image_group
from mtool.image.compress import image_compress_group

# Register compression tools with the main image group
image_group.add_command(image_compress_group) 