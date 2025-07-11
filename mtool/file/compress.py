"""
File compression tools
"""

import click
import os
import zipfile
import tarfile
import gzip
import bz2
import lzma
from pathlib import Path


@click.group(name="compress")
def compress_group():
    """
    Compress files and directories into various archive formats.
    
    Supports ZIP, TAR (with gzip/bzip2/xz compression), gzip, bzip2, and XZ formats.
    Can compress single files or entire directories with configurable compression levels.
    """
    pass


@compress_group.command(name="zip")
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--password", "-p", help="Password for encrypted archive")
def compress_zip(input_path, output_file, password):
    """
    Compress files/directories to ZIP format.
    """
    try:
        input_path = Path(input_path)
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if input_path.is_file():
                # Compress single file
                zipf.write(input_path, input_path.name)
            else:
                # Compress directory
                for file_path in input_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(input_path)
                        zipf.write(file_path, arcname)
        
        click.echo(f"Successfully compressed {input_path} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error compressing to ZIP: {e}", err=True)


@compress_group.command(name="tar")
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--format", "-f", type=click.Choice(['gz', 'bz2', 'xz']), default='gz', 
              help="Compression format")
def compress_tar(input_path, output_file, format):
    """
    Compress files/directories to TAR format with optional compression.
    """
    try:
        input_path = Path(input_path)
        
        # Determine compression mode
        if format == 'gz':
            mode = 'w:gz'
        elif format == 'bz2':
            mode = 'w:bz2'
        elif format == 'xz':
            mode = 'w:xz'
        else:
            mode = 'w'
        
        with tarfile.open(output_file, mode) as tar:
            tar.add(input_path, arcname=input_path.name)
        
        click.echo(f"Successfully compressed {input_path} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error compressing to TAR: {e}", err=True)


@compress_group.command(name="gzip")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--level", "-l", type=click.IntRange(1, 9), default=6, 
              help="Compression level (1-9)")
def compress_gzip(input_file, output_file, level):
    """
    Compress a single file using gzip compression.
    """
    try:
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb', compresslevel=level) as f_out:
                f_out.writelines(f_in)
        
        click.echo(f"Successfully compressed {input_file} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error compressing with gzip: {e}", err=True)


@compress_group.command(name="bzip2")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--level", "-l", type=click.IntRange(1, 9), default=6, 
              help="Compression level (1-9)")
def compress_bzip2(input_file, output_file, level):
    """
    Compress a single file using bzip2 compression.
    """
    try:
        with open(input_file, 'rb') as f_in:
            with bz2.open(output_file, 'wb', compresslevel=level) as f_out:
                f_out.writelines(f_in)
        
        click.echo(f"Successfully compressed {input_file} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error compressing with bzip2: {e}", err=True)


@compress_group.command(name="xz")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--level", "-l", type=click.IntRange(0, 9), default=6, 
              help="Compression level (0-9)")
def compress_xz(input_file, output_file, level):
    """
    Compress a single file using XZ compression.
    """
    try:
        with open(input_file, 'rb') as f_in:
            with lzma.open(output_file, 'wb', preset=level) as f_out:
                f_out.writelines(f_in)
        
        click.echo(f"Successfully compressed {input_file} to {output_file}")
        
    except Exception as e:
        click.echo(f"Error compressing with XZ: {e}", err=True) 