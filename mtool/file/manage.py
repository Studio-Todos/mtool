"""
File management tools for mtool
"""

import click
import os
import fnmatch
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

@click.group(name="manage")
def manage_group():
    """
    File management and organization tools.
    
    Find large or duplicate files, organize files by type, batch rename, search by name/content, and list recent files.
    """
    pass

@manage_group.command(name="find-large")
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--top", default=10, help="Show top N largest files")
def find_large(directory, top):
    """
    Find the largest files in a directory tree.
    """
    files = []
    for root, _, filenames in os.walk(directory):
        for fname in filenames:
            fpath = os.path.join(root, fname)
            try:
                size = os.path.getsize(fpath)
                files.append((size, fpath))
            except Exception:
                continue
    files.sort(reverse=True)
    click.echo(f"Top {top} largest files in {directory}:")
    for i, (size, fpath) in enumerate(files[:top], 1):
        click.echo(f"{i:2d}. {size/1024/1024:.2f} MB - {fpath}")

@manage_group.command(name="find-duplicates")
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
def find_duplicates(directory):
    """
    Find duplicate files by content hash in a directory tree.
    """
    hash_map = defaultdict(list)
    for root, _, filenames in os.walk(directory):
        for fname in filenames:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                hash_map[file_hash].append(fpath)
            except Exception:
                continue
    found = False
    for paths in hash_map.values():
        if len(paths) > 1:
            found = True
            click.echo("Duplicate files:")
            for p in paths:
                click.echo(f"  {p}")
            click.echo("")
    if not found:
        click.echo("No duplicate files found.")

@manage_group.command(name="organize")
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--by", type=click.Choice(['extension']), default='extension', help="Organize by file extension")
def organize_files(directory, by):
    """
    Organize files in a directory into subfolders by extension.
    """
    if by == 'extension':
        for item in Path(directory).iterdir():
            if item.is_file():
                ext = item.suffix[1:] if item.suffix else 'no_extension'
                target_dir = Path(directory) / ext
                target_dir.mkdir(exist_ok=True)
                shutil.move(str(item), str(target_dir / item.name))
        click.echo(f"Organized files in {directory} by extension.")

@manage_group.command(name="rename-batch")
@click.argument("pattern")
@click.argument("replacement")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), required=False, default='.')
def rename_batch(pattern, replacement, directory):
    """
    Batch rename files by pattern in a directory.
    """
    count = 0
    for root, _, filenames in os.walk(directory):
        for fname in filenames:
            if pattern in fname:
                new_name = fname.replace(pattern, replacement)
                src = os.path.join(root, fname)
                dst = os.path.join(root, new_name)
                os.rename(src, dst)
                click.echo(f"Renamed: {fname} -> {new_name}")
                count += 1
    if count == 0:
        click.echo("No files matched the pattern.")

@manage_group.command(name="search")
@click.argument("name_pattern")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), required=False, default='.')
def search_files(name_pattern, directory):
    """
    Search for files by name (supports wildcards).
    """
    matches = []
    for root, _, filenames in os.walk(directory):
        for fname in filenames:
            if fnmatch.fnmatch(fname, name_pattern):
                matches.append(os.path.join(root, fname))
    if matches:
        click.echo(f"Found {len(matches)} file(s):")
        for m in matches:
            click.echo(m)
    else:
        click.echo("No files found.")

@manage_group.command(name="search-content")
@click.argument("text")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), required=False, default='.')
def search_content(text, directory):
    """
    Search for text in file contents.
    """
    matches = []
    for root, _, filenames in os.walk(directory):
        for fname in filenames:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        if text in line:
                            matches.append((fpath, i, line.strip()))
            except Exception:
                continue
    if matches:
        click.echo(f"Found {len(matches)} match(es):")
        for fpath, i, line in matches:
            click.echo(f"{fpath}:{i}: {line}")
    else:
        click.echo("No matches found.")

@manage_group.command(name="recent")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), required=False, default='.')
@click.option("--days", default=7, help="Show files modified in the last N days")
def recent_files(directory, days):
    """
    Show files recently modified in the last N days.
    """
    cutoff = datetime.now() - timedelta(days=days)
    found = []
    for root, _, filenames in os.walk(directory):
        for fname in filenames:
            fpath = os.path.join(root, fname)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                if mtime > cutoff:
                    found.append((mtime, fpath))
            except Exception:
                continue
    found.sort(reverse=True)
    if found:
        click.echo(f"Files modified in the last {days} days:")
        for mtime, fpath in found:
            click.echo(f"{mtime.strftime('%Y-%m-%d %H:%M:%S')} - {fpath}")
    else:
        click.echo(f"No files modified in the last {days} days.") 