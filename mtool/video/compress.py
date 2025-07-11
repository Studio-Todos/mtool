"""
Video compression tools for mtool
"""

import click
import os
import subprocess
import math
import json

@click.group(name="compress")
def video_compress_group():
    """
    Video compression tools for social media and file size optimization.
    
    Compress videos to reduce file size by percentage or target specific file size.
    Useful for social media platforms with file size limits.
    """
    pass

def get_video_info(file_path):
    """Get video information using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception:
        return None

def get_video_size(file_path):
    """Get video file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

def compress_video_ffmpeg(input_file, output_file, target_bitrate=None, crf=None, preset='medium'):
    """Compress video using ffmpeg."""
    cmd = ['ffmpeg', '-i', input_file, '-y']  # -y to overwrite output
    
    if target_bitrate:
        cmd.extend(['-b:v', f'{target_bitrate}k'])
    if crf:
        cmd.extend(['-crf', str(crf)])
    
    cmd.extend(['-preset', preset, output_file])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

@video_compress_group.command(name="by-percent")
@click.argument("file", type=click.Path(exists=True))
@click.argument("reduction", type=click.IntRange(1, 99))
@click.option("--output", type=click.Path(), help="Output file (default: overwrite input)")
@click.option("--preset", default="medium", type=click.Choice(['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']), help="FFmpeg preset")
@click.option("--max-iterations", default=8, help="Maximum compression iterations")
def compress_by_percent(file, reduction, output, preset, max_iterations):
    """
    Compress video to reduce file size by specified percentage.
    
    Example: mtool video compress by-percent video.mp4 50
    """
    try:
        original_size = get_video_size(file)
        if original_size == 0:
            click.echo("Error: Could not read file size", err=True)
            return
        
        target_size = original_size * (1 - reduction / 100)
        
        click.echo(f"Original size: {original_size / 1024 / 1024:.1f} MB")
        click.echo(f"Target size: {target_size / 1024 / 1024:.1f} MB ({reduction}% reduction)")
        
        # Get video info
        video_info = get_video_info(file)
        if not video_info:
            click.echo("Error: Could not read video information", err=True)
            return
        
        # Find video stream
        video_stream = None
        for stream in video_info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        if not video_stream:
            click.echo("Error: No video stream found", err=True)
            return
        
        # Get original bitrate
        original_bitrate = int(video_info.get('format', {}).get('bit_rate', 0))
        if original_bitrate == 0:
            # Estimate bitrate from file size and duration
            duration = float(video_info.get('format', {}).get('duration', 1))
            original_bitrate = int((original_size * 8) / duration)  # bits per second
        
        # Start compression
        current_bitrate = original_bitrate
        iterations = 0
        
        while iterations < max_iterations:
            temp_output = f"{file}.temp{os.path.splitext(file)[1]}"
            
            # Calculate target bitrate for this iteration
            target_bitrate = int(current_bitrate * (target_size / original_size))
            
            click.echo(f"Iteration {iterations + 1}: Bitrate {target_bitrate}k, Size target: {target_size / 1024 / 1024:.1f} MB")
            
            # Compress video
            if compress_video_ffmpeg(file, temp_output, target_bitrate=target_bitrate, preset=preset):
                current_size = get_video_size(temp_output)
                click.echo(f"  Result: {current_size / 1024 / 1024:.1f} MB")
                
                if current_size <= target_size:
                    # Success! Move to final location
                    out_path = output or file
                    os.rename(temp_output, out_path)
                    break
                
                # Reduce bitrate for next iteration
                current_bitrate = int(current_bitrate * 0.8)
                iterations += 1
                
                # Clean up temp file
                os.remove(temp_output)
            else:
                click.echo("Error: FFmpeg compression failed", err=True)
                break
        
        if iterations >= max_iterations:
            click.echo("Warning: Could not achieve target size within iteration limit")
            if os.path.exists(temp_output):
                out_path = output or file
                os.rename(temp_output, out_path)
        
        final_size = get_video_size(output or file)
        actual_reduction = ((original_size - final_size) / original_size) * 100
        click.echo(f"Final size: {final_size / 1024 / 1024:.1f} MB")
        click.echo(f"Actual reduction: {actual_reduction:.1f}%")
        
    except Exception as e:
        click.echo(f"Error compressing video: {e}", err=True)

@video_compress_group.command(name="to-size")
@click.argument("file", type=click.Path(exists=True))
@click.argument("target_size_mb", type=click.IntRange(1))
@click.option("--output", type=click.Path(), help="Output file (default: overwrite input)")
@click.option("--preset", default="medium", type=click.Choice(['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']), help="FFmpeg preset")
@click.option("--max-iterations", default=10, help="Maximum compression iterations")
def compress_to_size(file, target_size_mb, output, preset, max_iterations):
    """
    Compress video to target file size in MB.
    
    Example: mtool video compress to-size video.mp4 50
    """
    try:
        original_size = get_video_size(file)
        if original_size == 0:
            click.echo("Error: Could not read file size", err=True)
            return
        
        target_size = target_size_mb * 1024 * 1024  # Convert MB to bytes
        
        if original_size <= target_size:
            click.echo(f"File is already smaller than target size ({original_size / 1024 / 1024:.1f} MB < {target_size_mb} MB)")
            return
        
        click.echo(f"Original size: {original_size / 1024 / 1024:.1f} MB")
        click.echo(f"Target size: {target_size_mb} MB")
        
        # Get video info
        video_info = get_video_info(file)
        if not video_info:
            click.echo("Error: Could not read video information", err=True)
            return
        
        # Find video stream
        video_stream = None
        for stream in video_info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        if not video_stream:
            click.echo("Error: No video stream found", err=True)
            return
        
        # Get original bitrate
        original_bitrate = int(video_info.get('format', {}).get('bit_rate', 0))
        if original_bitrate == 0:
            duration = float(video_info.get('format', {}).get('duration', 1))
            original_bitrate = int((original_size * 8) / duration)
        
        # Start compression
        current_bitrate = original_bitrate
        iterations = 0
        
        while iterations < max_iterations:
            temp_output = f"{file}.temp{os.path.splitext(file)[1]}"
            
            # Calculate target bitrate for this iteration
            target_bitrate = int(current_bitrate * (target_size / original_size))
            
            click.echo(f"Iteration {iterations + 1}: Bitrate {target_bitrate}k, Size target: {target_size / 1024 / 1024:.1f} MB")
            
            # Compress video
            if compress_video_ffmpeg(file, temp_output, target_bitrate=target_bitrate, preset=preset):
                current_size = get_video_size(temp_output)
                click.echo(f"  Result: {current_size / 1024 / 1024:.1f} MB")
                
                if current_size <= target_size:
                    out_path = output or file
                    os.rename(temp_output, out_path)
                    break
                
                current_bitrate = int(current_bitrate * 0.75)
                iterations += 1
                os.remove(temp_output)
            else:
                click.echo("Error: FFmpeg compression failed", err=True)
                break
        
        if iterations >= max_iterations:
            click.echo("Warning: Could not achieve target size within iteration limit")
            if os.path.exists(temp_output):
                out_path = output or file
                os.rename(temp_output, out_path)
        
        final_size = get_video_size(output or file)
        click.echo(f"Final size: {final_size / 1024 / 1024:.1f} MB")
        
    except Exception as e:
        click.echo(f"Error compressing video: {e}", err=True) 