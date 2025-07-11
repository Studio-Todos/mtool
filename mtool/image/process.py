"""
Image processing tools for mtool
"""

import click
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

@click.group()
def image_group():
    """
    Image processing tools: resize, watermark, optimize, info.
    """
    pass

@image_group.command(name="resize")
@click.argument("file", type=click.Path(exists=True))
@click.option("--size", required=True, help="New size as WIDTHxHEIGHT, e.g. 800x600")
@click.option("--output", type=click.Path(), help="Output file (default: overwrite input)")
def resize_image(file, size, output):
    """
    Resize an image to the specified size.
    """
    try:
        width, height = map(int, size.lower().split('x'))
        with Image.open(file) as img:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            out_path = output or file
            img.save(out_path)
        click.echo(f"Resized {file} to {width}x{height} -> {out_path}")
    except Exception as e:
        click.echo(f"Error resizing image: {e}", err=True)

@image_group.command(name="watermark")
@click.argument("file", type=click.Path(exists=True))
@click.option("--text", required=True, help="Watermark text")
@click.option("--output", type=click.Path(), help="Output file (default: overwrite input)")
def watermark_image(file, text, output):
    """
    Add a text watermark to an image.
    """
    try:
        with Image.open(file) as img:
            watermark = Image.new('RGBA', img.size, (0,0,0,0))
            draw = ImageDraw.Draw(watermark)
            font_size = int(min(img.size) / 8)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()
            textwidth, textheight = draw.textsize(text, font=font)
            x = (img.width - textwidth) // 2
            y = (img.height - textheight) // 2
            draw.text((x, y), text, font=font, fill=(255, 0, 0, 128))
            watermarked = Image.alpha_composite(img.convert('RGBA'), watermark)
            out_path = output or file
            watermarked = watermarked.convert(img.mode)
            watermarked.save(out_path)
        click.echo(f"Added watermark '{text}' to {file} -> {out_path}")
    except Exception as e:
        click.echo(f"Error adding watermark: {e}", err=True)

@image_group.command(name="optimize")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), help="Output file (default: overwrite input)")
@click.option("--quality", default=85, help="JPEG/WebP quality (default: 85)")
def optimize_image(file, output, quality):
    """
    Optimize/compress an image file (lossless for PNG, quality for JPEG/WebP).
    """
    try:
        with Image.open(file) as img:
            out_path = output or file
            ext = os.path.splitext(out_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.webp']:
                img.save(out_path, quality=quality, optimize=True)
            elif ext == '.png':
                img.save(out_path, optimize=True)
            else:
                img.save(out_path)
        click.echo(f"Optimized {file} -> {out_path}")
    except Exception as e:
        click.echo(f"Error optimizing image: {e}", err=True)

@image_group.command(name="info")
@click.argument("file", type=click.Path(exists=True))
def image_info(file):
    """
    Show image metadata and properties.
    """
    try:
        with Image.open(file) as img:
            click.echo(f"File: {file}")
            click.echo(f"Format: {img.format}")
            click.echo(f"Size: {img.size[0]}x{img.size[1]}")
            click.echo(f"Mode: {img.mode}")
            click.echo(f"Info: {img.info}")
            if hasattr(img, 'getexif'):
                exif = img.getexif()
                if exif:
                    click.echo("EXIF data:")
                    for tag, value in exif.items():
                        click.echo(f"  {tag}: {value}")
    except Exception as e:
        click.echo(f"Error reading image info: {e}", err=True) 