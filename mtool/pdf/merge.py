"""
PDF merge tool
"""

import click
from pathlib import Path

# Try to import PyPDF2, but make it optional
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


@click.group(name="merge")
def merge_group():
    """
    Merge multiple PDF files into one.
    """
    pass


@merge_group.command(name="files")
@click.argument("input_pdfs", nargs=-1, type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
def merge_pdfs(input_pdfs, output_pdf):
    """
    Merge multiple PDF files into one.
    
    Example: mtool pdf merge files file1.pdf file2.pdf file3.pdf output.pdf
    """
    if not PYPDF2_AVAILABLE:
        click.echo("Error: PDF processing requires PyPDF2. Install with: pip install PyPDF2", err=True)
        return
    
    if len(input_pdfs) < 2:
        click.echo("Error: At least 2 input PDF files are required.", err=True)
        return
    
    try:
        writer = PyPDF2.PdfWriter()
        total_pages = 0
        
        for pdf_file in input_pdfs:
            with open(pdf_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                pages = len(reader.pages)
                total_pages += pages
                
                for page in reader.pages:
                    writer.add_page(page)
                
                click.echo(f"Added {pdf_file} ({pages} pages)")
        
        # Write merged PDF
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)
        
        click.echo(f"Successfully merged {len(input_pdfs)} PDFs ({total_pages} total pages) into {output_pdf}")
        
    except Exception as e:
        click.echo(f"Error merging PDFs: {e}", err=True)


@merge_group.command(name="directory")
@click.argument("input_dir", type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
@click.option("--sort", is_flag=True, help="Sort files alphabetically before merging")
def merge_directory(input_dir, output_pdf, sort):
    """
    Merge all PDF files in a directory into one.
    """
    if not PYPDF2_AVAILABLE:
        click.echo("Error: PDF processing requires PyPDF2. Install with: pip install PyPDF2", err=True)
        return
    
    try:
        input_path = Path(input_dir)
        pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            click.echo(f"No PDF files found in {input_dir}", err=True)
            return
        
        if sort:
            pdf_files.sort()
        
        writer = PyPDF2.PdfWriter()
        total_pages = 0
        
        for pdf_file in pdf_files:
            with open(pdf_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                pages = len(reader.pages)
                total_pages += pages
                
                for page in reader.pages:
                    writer.add_page(page)
                
                click.echo(f"Added {pdf_file.name} ({pages} pages)")
        
        # Write merged PDF
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)
        
        click.echo(f"Successfully merged {len(pdf_files)} PDFs ({total_pages} total pages) into {output_pdf}")
        
    except Exception as e:
        click.echo(f"Error merging PDFs: {e}", err=True) 