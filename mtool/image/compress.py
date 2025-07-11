"""
Image compression tools for mtool
"""

import click
import os
from PIL import Image
import math

@click.group(name="compress")
def image_compress_group():
    """
    Image compression tools for social media and file size optimization.
    
    Compress images to reduce file size by percentage or target specific file size.
    Useful for social media platforms with file size limits.
    """
    pass

@image_compress_group.command(name="by-percent")
@click.argument("file", type=click.Path(exists=True))
@click.argument("reduction", type=click.IntRange(1, 99))
@click.option("--output", type=click.Path(), help="Output file (default: overwrite input)")
@click.option("--max-iterations", default=10, help="Maximum compression iterations")
def compress_by_percent(file, reduction, output, max_iterations):
    """
    Compress image to reduce file size by specified percentage.
    
    Example: mtool image compress by-percent photo.jpg 50
    """
    try:
        original_size = os.path.getsize(file)
        target_size = original_size * (1 - reduction / 100)
        
        click.echo(f"Original size: {original_size / 1024:.1f} KB")
        click.echo(f"Target size: {target_size / 1024:.1f} KB ({reduction}% reduction)")
        
        with Image.open(file) as img:
            # Start with high quality and reduce iteratively
            quality = 95
            current_size = original_size
            iterations = 0
            
            while current_size > target_size and iterations < max_iterations:
                # Create temporary file to check size
                temp_path = f"{file}.temp"
                
                # Save with current quality
                if file.lower().endswith(('.jpg', '.jpeg')):
                    img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                elif file.lower().endswith('.png'):
                    # For PNG, we need to reduce dimensions or convert to JPEG
                    if quality < 50:  # If quality is too low, reduce dimensions
                        scale_factor = math.sqrt(target_size / current_size)
                        new_width = int(img.width * scale_factor)
                        new_height = int(img.height * scale_factor)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        quality = 95  # Reset quality
                    else:
                        # Convert to JPEG for better compression
                        temp_path = temp_path.replace('.png', '.jpg')
                        img = img.convert('RGB')
                        img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                elif file.lower().endswith('.webp'):
                    img.save(temp_path, 'WebP', quality=quality, method=6)
                else:
                    # Convert to JPEG for other formats
                    temp_path = temp_path.replace(os.path.splitext(file)[1], '.jpg')
                    img = img.convert('RGB')
                    img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                
                current_size = os.path.getsize(temp_path)
                click.echo(f"Iteration {iterations + 1}: Quality {quality}, Size: {current_size / 1024:.1f} KB")
                
                if current_size <= target_size:
                    # Move temp file to final location
                    out_path = output or file
                    os.rename(temp_path, out_path)
                    break
                
                # Clean up temp file
                os.remove(temp_path)
                
                # Reduce quality for next iteration
                quality = max(5, quality - 10)
                iterations += 1
            
            if current_size > target_size:
                click.echo(f"Warning: Could not achieve target size. Final size: {current_size / 1024:.1f} KB")
                # Use the last attempt anyway
                out_path = output or file
                if os.path.exists(temp_path):
                    os.rename(temp_path, out_path)
            
            final_size = os.path.getsize(output or file)
            actual_reduction = ((original_size - final_size) / original_size) * 100
            click.echo(f"Final size: {final_size / 1024:.1f} KB")
            click.echo(f"Actual reduction: {actual_reduction:.1f}%")
            
    except Exception as e:
        click.echo(f"Error compressing image: {e}", err=True)

@image_compress_group.command(name="to-size")
@click.argument("file", type=click.Path(exists=True))
@click.argument("target_size_kb", type=click.IntRange(1))
@click.option("--output", type=click.Path(), help="Output file (default: overwrite input)")
@click.option("--max-iterations", default=15, help="Maximum compression iterations")
def compress_to_size(file, target_size_kb, output, max_iterations):
    """
    Compress image to target file size in KB.
    
    Example: mtool image compress to-size photo.jpg 500
    """
    try:
        original_size = os.path.getsize(file)
        target_size = target_size_kb * 1024  # Convert KB to bytes
        
        if original_size <= target_size:
            click.echo(f"File is already smaller than target size ({original_size / 1024:.1f} KB < {target_size_kb} KB)")
            return
        
        click.echo(f"Original size: {original_size / 1024:.1f} KB")
        click.echo(f"Target size: {target_size_kb} KB")
        
        with Image.open(file) as img:
            quality = 95
            current_size = original_size
            iterations = 0
            
            while current_size > target_size and iterations < max_iterations:
                temp_path = f"{file}.temp"
                
                # Save with current quality
                if file.lower().endswith(('.jpg', '.jpeg')):
                    img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                elif file.lower().endswith('.png'):
                    if quality < 30:  # If quality is very low, reduce dimensions
                        scale_factor = math.sqrt(target_size / current_size)
                        new_width = int(img.width * scale_factor)
                        new_height = int(img.height * scale_factor)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        quality = 95
                    else:
                        temp_path = temp_path.replace('.png', '.jpg')
                        img = img.convert('RGB')
                        img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                elif file.lower().endswith('.webp'):
                    img.save(temp_path, 'WebP', quality=quality, method=6)
                else:
                    temp_path = temp_path.replace(os.path.splitext(file)[1], '.jpg')
                    img = img.convert('RGB')
                    img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                
                current_size = os.path.getsize(temp_path)
                click.echo(f"Iteration {iterations + 1}: Quality {quality}, Size: {current_size / 1024:.1f} KB")
                
                if current_size <= target_size:
                    out_path = output or file
                    os.rename(temp_path, out_path)
                    break
                
                os.remove(temp_path)
                quality = max(5, quality - 8)
                iterations += 1
            
            if current_size > target_size:
                click.echo(f"Warning: Could not achieve target size. Final size: {current_size / 1024:.1f} KB")
                out_path = output or file
                if os.path.exists(temp_path):
                    os.rename(temp_path, out_path)
            
            final_size = os.path.getsize(output or file)
            click.echo(f"Final size: {final_size / 1024:.1f} KB")
            
    except Exception as e:
        click.echo(f"Error compressing image: {e}", err=True) 