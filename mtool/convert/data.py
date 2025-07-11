"""
Data conversion tools
"""

import click
import json
import csv
from pathlib import Path
from io import StringIO


@click.group(name="data")
def data_convert_group():
    """
    Data format conversion and manipulation tools.
    
    Convert between CSV and JSON formats with options for pretty printing, arrays,
    and flattening nested structures. Format and validate JSON files. Merge multiple
    CSV files and analyze CSV structure and content.
    """
    pass


@data_convert_group.command(name="csv-to-json")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--delimiter", "-d", default=",", help="CSV delimiter")
@click.option("--pretty", "-p", is_flag=True, help="Pretty print JSON")
@click.option("--array", "-a", is_flag=True, help="Output as JSON array instead of object")
def csv_to_json(input_file, output_file, delimiter, pretty, array):
    """
    Convert CSV file to JSON format.
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        # Read CSV
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            data = list(reader)
        
        if not data:
            click.echo("Warning: CSV file is empty", err=True)
            data = []
        
        # Convert to JSON
        if array:
            json_data = data
        else:
            # Convert to object with row numbers as keys
            json_data = {f"row_{i+1}": row for i, row in enumerate(data)}
        
        # Write JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(json_data, f, ensure_ascii=False)
        
        click.echo(f"✅ Converted {len(data)} rows from {input_path.name} to {output_path.name}")
        
    except Exception as e:
        click.echo(f"Error converting CSV to JSON: {e}", err=True)


@data_convert_group.command(name="json-to-csv")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--delimiter", "-d", default=",", help="CSV delimiter")
@click.option("--flatten", "-f", is_flag=True, help="Flatten nested JSON objects")
def json_to_csv(input_file, output_file, delimiter, flatten):
    """
    Convert JSON file to CSV format.
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        # Read JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            rows = data
        elif isinstance(data, dict):
            # If it's an object with numbered keys, extract the values
            if all(key.startswith('row_') for key in data.keys()):
                rows = list(data.values())
            else:
                # Single object, wrap in list
                rows = [data]
        else:
            click.echo("Error: JSON must be an object or array", err=True)
            return
        
        if not rows:
            click.echo("Warning: JSON data is empty", err=True)
            return
        
        # Flatten nested objects if requested
        if flatten:
            flattened_rows = []
            for row in rows:
                flattened = {}
                for key, value in row.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            flattened[f"{key}_{sub_key}"] = sub_value
                    elif isinstance(value, list):
                        flattened[key] = str(value)
                    else:
                        flattened[key] = value
                flattened_rows.append(flattened)
            rows = flattened_rows
        
        # Get all unique field names
        fieldnames = set()
        for row in rows:
            fieldnames.update(row.keys())
        fieldnames = sorted(fieldnames)
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(rows)
        
        click.echo(f"✅ Converted {len(rows)} rows from {input_path.name} to {output_path.name}")
        
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON format - {e}", err=True)
    except Exception as e:
        click.echo(f"Error converting JSON to CSV: {e}", err=True)


@data_convert_group.command(name="format-json")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--indent", "-i", default=2, help="Indentation spaces")
@click.option("--sort-keys", "-s", is_flag=True, help="Sort object keys")
def format_json(input_file, output_file, indent, sort_keys):
    """
    Format JSON file with proper indentation and optional key sorting.
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        # Read JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Write formatted JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, sort_keys=sort_keys)
        
        click.echo(f"✅ Formatted JSON from {input_path.name} to {output_path.name}")
        
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON format - {e}", err=True)
    except Exception as e:
        click.echo(f"Error formatting JSON: {e}", err=True)


@data_convert_group.command(name="validate-json")
@click.argument("input_file", type=click.Path(exists=True))
def validate_json(input_file):
    """
    Validate JSON file format.
    """
    try:
        input_path = Path(input_file)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Count elements
        if isinstance(data, list):
            count = len(data)
            data_type = "array"
        elif isinstance(data, dict):
            count = len(data)
            data_type = "object"
        else:
            count = 1
            data_type = "value"
        
        click.echo(f"✅ Valid JSON: {data_type} with {count} elements")
        
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}", err=True)
    except Exception as e:
        click.echo(f"Error validating JSON: {e}", err=True)


@data_convert_group.command(name="csv-info")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--delimiter", "-d", default=",", help="CSV delimiter")
def csv_info(input_file, delimiter):
    """
    Show information about CSV file.
    """
    try:
        input_path = Path(input_file)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
        
        if not rows:
            click.echo("CSV file is empty")
            return
        
        headers = rows[0]
        data_rows = rows[1:]
        
        click.echo(f"📊 CSV File: {input_path.name}")
        click.echo(f"   Rows: {len(data_rows)}")
        click.echo(f"   Columns: {len(headers)}")
        click.echo(f"   Headers: {', '.join(headers)}")
        
        # Show sample data
        if data_rows:
            click.echo(f"   Sample data (first 3 rows):")
            for i, row in enumerate(data_rows[:3]):
                click.echo(f"     Row {i+1}: {row}")
        
    except Exception as e:
        click.echo(f"Error reading CSV: {e}", err=True)


@data_convert_group.command(name="merge-csv")
@click.argument("input_files", nargs=-1, type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--delimiter", "-d", default=",", help="CSV delimiter")
@click.option("--headers", is_flag=True, help="Include headers in output")
def merge_csv(input_files, output_file, delimiter, headers):
    """
    Merge multiple CSV files into one.
    """
    try:
        if len(input_files) < 2:
            click.echo("Error: At least 2 input files required", err=True)
            return
        
        output_path = Path(output_file)
        all_rows = []
        total_rows = 0
        
        for input_file in input_files:
            input_path = Path(input_file)
            click.echo(f"Reading {input_path.name}...")
            
            with open(input_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
                
                if rows:
                    if headers and all_rows:
                        # Skip header for subsequent files
                        rows = rows[1:]
                    elif not headers and not all_rows:
                        # Include header only from first file
                        all_rows.append(rows[0])
                        rows = rows[1:]
                    
                    all_rows.extend(rows)
                    total_rows += len(rows)
        
        # Write merged CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerows(all_rows)
        
        click.echo(f"✅ Merged {len(input_files)} files with {total_rows} total rows to {output_path.name}")
        
    except Exception as e:
        click.echo(f"Error merging CSV files: {e}", err=True) 