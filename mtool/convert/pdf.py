"""
PDF conversion tools
"""

import click
from pathlib import Path
from PIL import Image

# Try to import PyPDF2, but make it optional
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# Try to import pdf2image for PDF to image conversion
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


@click.group(name="pdf")
def pdf_convert_group():
    """
    Convert between PDF documents and other formats.
    
    Convert multiple images to PDF documents. Convert PDF pages to images (PNG, JPG)
    with configurable DPI. Extract text content from PDF files to plain text.
    """
    pass


@pdf_convert_group.command(name="images-to-pdf")
@click.argument("image_files", nargs=-1, type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
@click.option("--page-size", default="A4", help="Page size (A4, Letter, etc.)")
def images_to_pdf(image_files, output_pdf, page_size):
    """
    Convert multiple images to a single PDF.
    
    Example: mtool convert pdf images-to-pdf image1.jpg image2.png output.pdf
    """
    if not image_files:
        click.echo("Error: At least one image file is required.", err=True)
        return
    
    try:
        # Convert images to RGB if needed and create PDF
        images = []
        for img_file in image_files:
            with Image.open(img_file) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                images.append(img.copy())
        
        # Save first image as PDF, then append others
        if images:
            images[0].save(output_pdf, "PDF", save_all=True, append_images=images[1:])
            click.echo(f"Successfully converted {len(image_files)} images to {output_pdf}")
        else:
            click.echo("Error: No valid images found.", err=True)
            
    except Exception as e:
        click.echo(f"Error converting images to PDF: {e}", err=True)


@pdf_convert_group.command(name="pdf-to-images")
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path(), default=".")
@click.option("--format", "-f", default="png", type=click.Choice(['png', 'jpg', 'jpeg']), 
              help="Output image format")
@click.option("--dpi", default=200, type=int, help="DPI for image conversion")
def pdf_to_images(input_pdf, output_dir, format, dpi):
    """
    Convert PDF pages to images.
    """
    if not PDF2IMAGE_AVAILABLE:
        click.echo("Error: PDF to image conversion requires pdf2image. Install with: pip install pdf2image", err=True)
        return
    
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        input_path = Path(input_pdf)
        base_name = input_path.stem
        
        # Convert PDF to images
        images = convert_from_path(input_pdf, dpi=dpi)
        
        for i, image in enumerate(images):
            output_file = output_path / f"{base_name}_page_{i + 1}.{format}"
            image.save(output_file, format.upper())
        
        click.echo(f"Successfully converted {input_pdf} to {len(images)} images in {output_dir}")
        
    except Exception as e:
        click.echo(f"Error converting PDF to images: {e}", err=True)


@pdf_convert_group.command(name="extract-text")
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_txt", type=click.Path())
def extract_text(input_pdf, output_txt):
    """
    Extract text from PDF to a text file.
    """
    if not PYPDF2_AVAILABLE:
        click.echo("Error: PDF text extraction requires PyPDF2. Install with: pip install PyPDF2", err=True)
        return
    
    try:
        with open(input_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            with open(output_txt, 'w', encoding='utf-8') as output_file:
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        output_file.write(f"--- Page {page_num} ---\n")
                        output_file.write(text)
                        output_file.write("\n\n")
        
        click.echo(f"Successfully extracted text from {input_pdf} to {output_txt}")
        
    except Exception as e:
        click.echo(f"Error extracting text: {e}", err=True) 