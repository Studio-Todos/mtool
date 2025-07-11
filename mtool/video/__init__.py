"""
Video processing tools for mtool
"""

import click
from mtool.video.compress import video_compress_group

@click.group(name="video")
def video_group():
    """
    Video processing and compression tools.
    
    Compress videos to reduce file size by percentage or target specific file size.
    Useful for social media platforms with file size limits.
    """
    pass

# Register compression tools
video_group.add_command(video_compress_group) 