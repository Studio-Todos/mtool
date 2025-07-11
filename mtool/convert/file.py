"""
File conversion tools
"""

import click
import os
from pathlib import Path
from PIL import Image

# Try to import pydub, but make it optional
try:
    import pydub
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


@click.group(name="file")
def file_convert_group():
    """
    Convert media files between different formats.
    
    Convert images (JPG, PNG, GIF, BMP, TIFF, WebP) with quality and resize options.
    Convert audio files (MP3, WAV, FLAC, OGG, AAC) with bitrate and sample rate control.
    Convert video files (MP4, AVI, MOV, MKV, WebM) using ffmpeg with codec and resolution options.
    """
    pass


@file_convert_group.command(name="image")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--quality", "-q", default=95, help="Image quality (1-100)")
@click.option("--resize", "-r", help="Resize image (e.g., 800x600)")
def convert_image(input_file, output_file, quality, resize):
    """
    Convert image files between formats.
    
    Supported formats: JPG, PNG, GIF, BMP, TIFF, WebP
    """
    try:
        # Open image
        with Image.open(input_file) as img:
            # Convert to RGB if necessary (for JPEG)
            if output_file.lower().endswith('.jpg') or output_file.lower().endswith('.jpeg'):
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
            
            # Handle resize if specified
            if resize:
                try:
                    width, height = map(int, resize.split('x'))
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                except ValueError:
                    click.echo("Error: Resize format should be WIDTHxHEIGHT (e.g., 800x600)")
                    return
            
            # Save with quality setting
            img.save(output_file, quality=quality, optimize=True)
            
        click.echo(f"Successfully converted {input_file} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error converting image: {e}", err=True)


@file_convert_group.command(name="audio")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--bitrate", "-b", help="Audio bitrate (e.g., 192k)")
@click.option("--sample-rate", "-s", type=int, help="Sample rate in Hz")
def convert_audio(input_file, output_file, bitrate, sample_rate):
    """
    Convert audio files between formats.
    
    Supported formats: MP3, WAV, FLAC, OGG, AAC
    """
    if not PYDUB_AVAILABLE:
        click.echo("Error: Audio conversion requires pydub library. Please install it with: pip install pydub", err=True)
        return
    
    try:
        # Load audio file
        audio = pydub.AudioSegment.from_file(input_file)
        
        # Apply sample rate conversion if specified
        if sample_rate:
            audio = audio.set_frame_rate(sample_rate)
        
        # Export with specified parameters
        export_params = {}
        if bitrate:
            export_params['bitrate'] = bitrate
        
        audio.export(output_file, **export_params)
        
        click.echo(f"Successfully converted {input_file} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error converting audio: {e}", err=True)


@file_convert_group.command(name="video")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--codec", "-c", help="Video codec (e.g., h264, h265)")
@click.option("--resolution", "-r", help="Video resolution (e.g., 1920x1080)")
def convert_video(input_file, output_file, codec, resolution):
    """
    Convert video files between formats.
    
    Note: This requires ffmpeg to be installed on the system.
    Supported formats: MP4, AVI, MOV, MKV, WebM
    """
    try:
        import subprocess
        
        # Build ffmpeg command
        cmd = ["ffmpeg", "-i", input_file]
        
        if codec:
            cmd.extend(["-c:v", codec])
        
        if resolution:
            cmd.extend(["-s", resolution])
        
        cmd.append(output_file)
        
        # Run ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo(f"Successfully converted {input_file} to {output_file}")
        else:
            click.echo(f"Error converting video: {result.stderr}", err=True)
            
    except ImportError:
        click.echo("Error: ffmpeg is required for video conversion. Please install ffmpeg.", err=True)
    except Exception as e:
        click.echo(f"Error converting video: {e}", err=True) 