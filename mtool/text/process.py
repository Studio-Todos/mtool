"""
Text processing tools
"""

import click
import re
from pathlib import Path
from collections import Counter


@click.group(name="process")
def process_group():
    """
    Text processing, analysis, and manipulation operations.
    
    Count lines, words, characters, and bytes in text files. Search for text patterns
    with regex support and line number display. Find and replace text with backup
    options and dry-run preview. Sort lines alphabetically or numerically with
    duplicate removal. Generate text statistics and word frequency analysis.
    """
    pass


@process_group.command(name="count")
@click.argument("file", type=click.Path(exists=True))
@click.option("--lines", "-l", is_flag=True, help="Count lines")
@click.option("--words", "-w", is_flag=True, help="Count words")
@click.option("--chars", "-c", is_flag=True, help="Count characters")
@click.option("--bytes", "-b", is_flag=True, help="Count bytes")
def count_text(file, lines, words, chars, bytes):
    """
    Count lines, words, characters, or bytes in a file.
    """
    try:
        file_path = Path(file)
        
        # If no specific option is given, show all counts
        if not any([lines, words, chars, bytes]):
            lines = words = chars = bytes = True
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        click.echo(f"File: {file_path.name}")
        
        if lines:
            line_count = len(content.splitlines())
            click.echo(f"Lines: {line_count}")
        
        if words:
            word_count = len(content.split())
            click.echo(f"Words: {word_count}")
        
        if chars:
            char_count = len(content)
            click.echo(f"Characters: {char_count}")
        
        if bytes:
            byte_count = len(content.encode('utf-8'))
            click.echo(f"Bytes: {byte_count}")
            
    except Exception as e:
        click.echo(f"Error counting text: {e}", err=True)


@process_group.command(name="search")
@click.argument("pattern")
@click.argument("file", type=click.Path(exists=True))
@click.option("--case-sensitive", "-c", is_flag=True, help="Case sensitive search")
@click.option("--regex", "-r", is_flag=True, help="Use regex pattern")
@click.option("--line-numbers", "-n", is_flag=True, help="Show line numbers")
@click.option("--count-only", is_flag=True, help="Show only count of matches")
def search_text(pattern, file, case_sensitive, regex, line_numbers, count_only):
    """
    Search for text patterns in a file.
    """
    try:
        file_path = Path(file)
        
        # Prepare pattern
        if regex:
            search_pattern = re.compile(pattern, flags=0 if case_sensitive else re.IGNORECASE)
        else:
            if not case_sensitive:
                pattern = pattern.lower()
            search_pattern = pattern
        
        matches = []
        match_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                search_line = line if case_sensitive else line.lower()
                
                if regex:
                    if search_pattern.search(search_line):
                        matches.append((line_num, line.rstrip()))
                        match_count += 1
                else:
                    if pattern in search_line:
                        matches.append((line_num, line.rstrip()))
                        match_count += 1
        
        if count_only:
            click.echo(f"Found {match_count} matches")
        else:
            if matches:
                click.echo(f"Found {match_count} matches in {file_path.name}:")
                click.echo("-" * 50)
                
                for line_num, line in matches:
                    if line_numbers:
                        click.echo(f"{line_num:4d}: {line}")
                    else:
                        click.echo(line)
            else:
                click.echo("No matches found")
                
    except re.error as e:
        click.echo(f"Invalid regex pattern: {e}", err=True)
    except Exception as e:
        click.echo(f"Error searching text: {e}", err=True)


@process_group.command(name="replace")
@click.argument("old_text")
@click.argument("new_text")
@click.argument("file", type=click.Path(exists=True))
@click.option("--case-sensitive", "-c", is_flag=True, help="Case sensitive replacement")
@click.option("--regex", "-r", is_flag=True, help="Use regex pattern")
@click.option("--backup", "-b", is_flag=True, help="Create backup file")
@click.option("--dry-run", "-d", is_flag=True, help="Show what would be changed without making changes")
def replace_text(old_text, new_text, file, case_sensitive, regex, backup, dry_run):
    """
    Find and replace text in a file.
    """
    try:
        file_path = Path(file)
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Prepare pattern
        if regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            content = re.sub(old_text, new_text, content, flags=flags)
        else:
            if not case_sensitive:
                # Case insensitive replacement
                import re
                pattern = re.compile(re.escape(old_text), re.IGNORECASE)
                content = pattern.sub(new_text, content)
            else:
                content = content.replace(old_text, new_text)
        
        # Count changes
        changes = len(original_content.split(old_text)) - 1 if not regex else len(re.findall(old_text, original_content, flags=0 if case_sensitive else re.IGNORECASE))
        
        if dry_run:
            click.echo(f"Would replace {changes} occurrences")
            if changes > 0:
                click.echo("Sample changes:")
                # Show first few lines with changes
                original_lines = original_content.splitlines()
                new_lines = content.splitlines()
                
                for i, (orig_line, new_line) in enumerate(zip(original_lines, new_lines)):
                    if orig_line != new_line:
                        click.echo(f"Line {i+1}:")
                        click.echo(f"  - {orig_line}")
                        click.echo(f"  + {new_line}")
                        if i >= 2:  # Show max 3 changes
                            break
        else:
            if changes > 0:
                # Create backup if requested
                if backup:
                    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    click.echo(f"Backup created: {backup_path}")
                
                # Write changes
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                click.echo(f"✅ Replaced {changes} occurrences in {file_path.name}")
            else:
                click.echo("No occurrences found to replace")
                
    except re.error as e:
        click.echo(f"Invalid regex pattern: {e}", err=True)
    except Exception as e:
        click.echo(f"Error replacing text: {e}", err=True)


@process_group.command(name="sort")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file (default: overwrite input)")
@click.option("--reverse", "-r", is_flag=True, help="Sort in reverse order")
@click.option("--numeric", "-n", is_flag=True, help="Sort numerically")
@click.option("--unique", "-u", is_flag=True, help="Remove duplicate lines")
def sort_text(file, output, reverse, numeric, unique):
    """
    Sort lines in a file.
    """
    try:
        file_path = Path(file)
        
        # Read lines
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove duplicates if requested
        if unique:
            lines = list(dict.fromkeys(lines))  # Preserve order
        
        # Sort lines
        if numeric:
            # Try to sort numerically, fall back to string sort
            try:
                lines.sort(key=lambda x: float(x.strip()), reverse=reverse)
            except ValueError:
                lines.sort(key=lambda x: x.strip(), reverse=reverse)
        else:
            lines.sort(key=lambda x: x.strip(), reverse=reverse)
        
        # Determine output file
        output_path = Path(output) if output else file_path
        
        # Write sorted lines
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        click.echo(f"✅ Sorted {len(lines)} lines in {output_path.name}")
        
    except Exception as e:
        click.echo(f"Error sorting text: {e}", err=True)


@process_group.command(name="dedupe")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file (default: overwrite input)")
@click.option("--case-insensitive", "-i", is_flag=True, help="Case insensitive deduplication")
@click.option("--count", "-c", is_flag=True, help="Show count of duplicates removed")
def dedupe_text(file, output, case_insensitive, count):
    """
    Remove duplicate lines from a file.
    """
    try:
        file_path = Path(file)
        
        # Read lines
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_count = len(lines)
        
        # Remove duplicates
        if case_insensitive:
            seen = set()
            unique_lines = []
            for line in lines:
                line_lower = line.lower()
                if line_lower not in seen:
                    seen.add(line_lower)
                    unique_lines.append(line)
            lines = unique_lines
        else:
            lines = list(dict.fromkeys(lines))  # Preserve order
        
        final_count = len(lines)
        removed_count = original_count - final_count
        
        # Determine output file
        output_path = Path(output) if output else file_path
        
        # Write deduplicated lines
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        if count:
            click.echo(f"✅ Removed {removed_count} duplicate lines")
            click.echo(f"Original: {original_count} lines")
            click.echo(f"Final: {final_count} lines")
        else:
            click.echo(f"✅ Removed duplicates from {output_path.name}")
        
    except Exception as e:
        click.echo(f"Error deduplicating text: {e}", err=True)


@process_group.command(name="stats")
@click.argument("file", type=click.Path(exists=True))
@click.option("--top", "-t", default=10, help="Show top N most common words")
def text_stats(file, top):
    """
    Show text statistics including word frequency.
    """
    try:
        file_path = Path(file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic stats
        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)
        bytes_size = len(content.encode('utf-8'))
        
        click.echo(f"File: {file_path.name}")
        click.echo(f"Lines: {lines}")
        click.echo(f"Words: {words}")
        click.echo(f"Characters: {chars}")
        click.echo(f"Bytes: {bytes_size}")
        
        # Word frequency
        if words > 0:
            # Clean words (remove punctuation, convert to lowercase)
            import re
            clean_words = re.findall(r'\b\w+\b', content.lower())
            word_freq = Counter(clean_words)
            
            click.echo(f"\nTop {top} most common words:")
            for word, count in word_freq.most_common(top):
                percentage = (count / len(clean_words)) * 100
                click.echo(f"  {word}: {count} ({percentage:.1f}%)")
        
    except Exception as e:
        click.echo(f"Error analyzing text: {e}", err=True) 