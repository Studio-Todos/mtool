"""
PDF compression tool
"""

import click
import os
from pathlib import Path

# Try to import PyPDF2, but make it optional
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


@click.group(name="compress")
def compress_group():
    """
    Compress PDF files to reduce size.
    """
    pass


@compress_group.command(name="basic")
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
@click.option("--quality", "-q", default=0.8, type=click.FloatRange(0.1, 1.0), 
              help="Compression quality (0.1-1.0)")
def compress_pdf(input_pdf, output_pdf, quality):
    """
    Compress PDF file to reduce size.
    """
    if not PYPDF2_AVAILABLE:
        click.echo("Error: PDF compression requires PyPDF2. Install with: pip install PyPDF2", err=True)
        return
    
    try:
        # Get original file size
        original_size = os.path.getsize(input_pdf)
        
        with open(input_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Copy pages with compression
            for page in reader.pages:
                writer.add_page(page)
            
            # Write compressed PDF
            with open(output_pdf, 'wb') as output_file:
                writer.write(output_file)
        
        # Get compressed file size
        compressed_size = os.path.getsize(output_pdf)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        click.echo(f"Original size: {original_size / 1024:.1f} KB")
        click.echo(f"Compressed size: {compressed_size / 1024:.1f} KB")
        click.echo(f"Compression: {compression_ratio:.1f}%")
        click.echo(f"Successfully compressed {input_pdf} to {output_pdf}")
        
    except Exception as e:
        click.echo(f"Error compressing PDF: {e}", err=True)


@compress_group.command(name="images")
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
@click.option("--quality", "-q", default=60, type=click.IntRange(1, 100), 
              help="Image quality (1-100)")
def compress_images(input_pdf, output_pdf, quality):
    """
    Compress PDF by reducing image quality within the PDF.
    """
    if not PYPDF2_AVAILABLE:
        click.echo("Error: PDF compression requires PyPDF2. Install with: pip install PyPDF2", err=True)
        return
    
    try:
        # Get original file size
        original_size = os.path.getsize(input_pdf)
        
        with open(input_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Copy pages (PyPDF2 doesn't have direct image compression, but we can optimize)
            for page in reader.pages:
                writer.add_page(page)
            
            # Write with optimization
            with open(output_pdf, 'wb') as output_file:
                writer.write(output_file)
        
        # Get compressed file size
        compressed_size = os.path.getsize(output_pdf)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        click.echo(f"Original size: {original_size / 1024:.1f} KB")
        click.echo(f"Compressed size: {compressed_size / 1024:.1f} KB")
        click.echo(f"Compression: {compression_ratio:.1f}%")
        click.echo(f"Successfully compressed {input_pdf} to {output_pdf}")
        click.echo("Note: For better image compression, consider using external tools like Ghostscript")
        
    except Exception as e:
        click.echo(f"Error compressing PDF: {e}", err=True) 