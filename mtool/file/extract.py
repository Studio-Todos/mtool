"""
File extraction tools
"""

import click
import os
import zipfile
import tarfile
import gzip
import bz2
import lzma
from pathlib import Path


@click.group(name="extract")
def extract_group():
    """
    Extract compressed files and archives with automatic format detection.
    
    Supports ZIP, TAR (with various compression), gzip, bzip2, and XZ formats.
    Can automatically detect file format or specify format explicitly.
    """
    pass


@extract_group.command(name="zip")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path(), default=".")
@click.option("--password", "-p", help="Password for encrypted archive")
def extract_zip(input_file, output_dir, password):
    """
    Extract ZIP archives.
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(input_file, 'r') as zipf:
            if password:
                zipf.extractall(output_path, pwd=password.encode())
            else:
                zipf.extractall(output_path)
        
        click.echo(f"Successfully extracted {input_file} to {output_dir}")
        
    except zipfile.BadZipFile:
        click.echo("Error: Invalid ZIP file", err=True)
    except Exception as e:
        click.echo(f"Error extracting ZIP: {e}", err=True)


@extract_group.command(name="tar")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path(), default=".")
def extract_tar(input_file, output_dir):
    """
    Extract TAR archives (including compressed variants).
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with tarfile.open(input_file, 'r:*') as tar:
            tar.extractall(output_path)
        
        click.echo(f"Successfully extracted {input_file} to {output_dir}")
        
    except Exception as e:
        click.echo(f"Error extracting TAR: {e}", err=True)


@extract_group.command(name="gzip")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def extract_gzip(input_file, output_file):
    """
    Extract gzip compressed files.
    """
    try:
        with gzip.open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        click.echo(f"Successfully extracted {input_file} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error extracting gzip: {e}", err=True)


@extract_group.command(name="bzip2")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def extract_bzip2(input_file, output_file):
    """
    Extract bzip2 compressed files.
    """
    try:
        with bz2.open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        click.echo(f"Successfully extracted {input_file} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error extracting bzip2: {e}", err=True)


@extract_group.command(name="xz")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def extract_xz(input_file, output_file):
    """
    Extract XZ compressed files.
    """
    try:
        with lzma.open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        click.echo(f"Successfully extracted {input_file} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error extracting XZ: {e}", err=True)


@extract_group.command(name="auto")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path(), default=".")
def extract_auto(input_file, output_dir):
    """
    Automatically detect and extract compressed files.
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Detect file type by extension
        suffix = input_path.suffix.lower()
        
        if suffix == '.zip':
            with zipfile.ZipFile(input_file, 'r') as zipf:
                zipf.extractall(output_path)
        elif suffix in ['.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz']:
            with tarfile.open(input_file, 'r:*') as tar:
                tar.extractall(output_path)
        elif suffix == '.gz':
            output_file = output_path / input_path.stem
            with gzip.open(input_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    f_out.write(f_in.read())
        elif suffix == '.bz2':
            output_file = output_path / input_path.stem
            with bz2.open(input_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    f_out.write(f_in.read())
        elif suffix == '.xz':
            output_file = output_path / input_path.stem
            with lzma.open(input_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    f_out.write(f_in.read())
        else:
            click.echo(f"Error: Unsupported file format: {suffix}", err=True)
            return
        
        click.echo(f"Successfully extracted {input_file} to {output_dir}")
        
    except Exception as e:
        click.echo(f"Error extracting file: {e}", err=True) 