"""
QR code generator tool for mtool
"""

import click
import qrcode
import sys
from io import BytesIO

@click.group(name="qrcode")
def qrcode_group():
    """
    Generate QR codes from text or URLs with terminal display.
    
    Create QR codes from any text or URL and display them as ASCII art in the terminal.
    Optionally save QR codes as PNG image files for sharing or printing.
    """
    pass

@qrcode_group.command(name="generate")
@click.argument("text")
def generate_qrcode(text):
    """
    Generate a QR code from TEXT and display it in the terminal. Optionally save as PNG.
    """
    try:
        qr = qrcode.QRCode(border=1)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Print QR code in terminal (ASCII)
        ascii_img = qr.get_matrix()
        for row in ascii_img:
            print(''.join(['  ' if cell else '██' for cell in row]))

        # Prompt user to save
        save_response = input("\nSave QR code as PNG? (y/n): ").lower().strip()
        if save_response in ['y', 'yes']:
            filename = "qrcode.png"
            img.save(filename)
            click.echo(f"QR code saved as {filename}")
        else:
            click.echo("QR code not saved.")
    except Exception as e:
        click.echo(f"Error generating QR code: {e}", err=True) 