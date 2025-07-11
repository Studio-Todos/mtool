"""
PDF split tool
"""

import click
import re
from pathlib import Path

# Try to import PyPDF2, but make it optional
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


@click.group(name="split")
def split_group():
    """
    Split PDF files by pages.
    """
    pass


def parse_page_ranges(page_ranges_str):
    """Parse page ranges like '1-3,5,7-10' into list of page numbers."""
    pages = []
    ranges = page_ranges_str.split(',')
    
    for range_str in ranges:
        range_str = range_str.strip()
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(range_str))
    
    return sorted(set(pages))  # Remove duplicates and sort


@split_group.command(name="pages")
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
@click.argument("page_ranges", type=str)
def split_pages(input_pdf, output_pdf, page_ranges):
    """
    Extract specific pages from a PDF.
    
    PAGE_RANGES format: '1-3,5,7-10' (extract pages 1,2,3,5,7,8,9,10)
    """
    if not PYPDF2_AVAILABLE:
        click.echo("Error: PDF processing requires PyPDF2. Install with: pip install PyPDF2", err=True)
        return
    
    try:
        # Parse page ranges
        try:
            page_numbers = parse_page_ranges(page_ranges)
        except ValueError:
            click.echo("Error: Invalid page range format. Use format like '1-3,5,7-10'", err=True)
            return
        
        # Read input PDF
        with open(input_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            # Validate page numbers
            invalid_pages = [p for p in page_numbers if p < 1 or p > total_pages]
            if invalid_pages:
                click.echo(f"Error: Invalid page numbers: {invalid_pages}. PDF has {total_pages} pages.", err=True)
                return
            
            # Create new PDF with selected pages
            writer = PyPDF2.PdfWriter()
            
            for page_num in page_numbers:
                # PyPDF2 uses 0-based indexing
                page = reader.pages[page_num - 1]
                writer.add_page(page)
            
            # Write output PDF
            with open(output_pdf, 'wb') as output_file:
                writer.write(output_file)
            
            click.echo(f"Successfully extracted pages {page_ranges} from {input_pdf} to {output_pdf}")
            
    except Exception as e:
        click.echo(f"Error splitting PDF: {e}", err=True)


@split_group.command(name="all")
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path(), default=".")
def split_all_pages(input_pdf, output_dir):
    """
    Split PDF into individual pages.
    """
    if not PYPDF2_AVAILABLE:
        click.echo("Error: PDF processing requires PyPDF2. Install with: pip install PyPDF2", err=True)
        return
    
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        input_path = Path(input_pdf)
        base_name = input_path.stem
        
        with open(input_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            for page_num in range(total_pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                output_file = output_path / f"{base_name}_page_{page_num + 1}.pdf"
                with open(output_file, 'wb') as output_file_handle:
                    writer.write(output_file_handle)
            
            click.echo(f"Successfully split {input_pdf} into {total_pages} individual pages in {output_dir}")
            
    except Exception as e:
        click.echo(f"Error splitting PDF: {e}", err=True) 