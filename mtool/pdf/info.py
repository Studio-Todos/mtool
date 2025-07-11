"""
PDF info tool
"""

import click
import os
from pathlib import Path
from datetime import datetime

# Try to import PyPDF2, but make it optional
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# Try to import pdfplumber as alternative
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


@click.group(name="info")
def info_group():
    """
    Get information about PDF files.
    """
    pass


@info_group.command(name="show")
@click.argument("pdf_file", type=click.Path(exists=True))
def show_pdf_info(pdf_file):
    """
    Show detailed information about a PDF file.
    """
    if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
        click.echo("Error: PDF processing requires PyPDF2 or pdfplumber. Install with: pip install PyPDF2", err=True)
        return
    
    try:
        pdf_path = Path(pdf_file)
        
        # Basic file info
        file_size = pdf_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        modified_time = datetime.fromtimestamp(pdf_path.stat().st_mtime)
        
        click.echo(f"File: {pdf_path.name}")
        click.echo(f"Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
        click.echo(f"Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo()
        
        # PDF-specific info
        if PYPDF2_AVAILABLE:
            try:
                with open(pdf_file, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    
                    click.echo(f"Pages: {len(reader.pages)}")
                    
                    if reader.metadata:
                        click.echo("Metadata:")
                        for key, value in reader.metadata.items():
                            if value:
                                click.echo(f"  {key}: {value}")
                    else:
                        click.echo("No metadata found")
                        
            except Exception as e:
                click.echo(f"Error reading PDF with PyPDF2: {e}", err=True)
                
        elif PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    click.echo(f"Pages: {len(pdf.pages)}")
                    
                    # Show page dimensions for first page
                    if pdf.pages:
                        first_page = pdf.pages[0]
                        width = first_page.width
                        height = first_page.height
                        click.echo(f"Page size: {width:.1f} x {height:.1f} points")
                        
            except Exception as e:
                click.echo(f"Error reading PDF with pdfplumber: {e}", err=True)
                
    except Exception as e:
        click.echo(f"Error getting PDF info: {e}", err=True) 