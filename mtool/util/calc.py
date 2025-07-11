"""
Calculator and conversion tools for mtool
"""

import click
import base64
import re
import math
from typing import Dict, Any, Callable


@click.group(name="calc")
def calc_group():
    """
    Simple arithmetic calculator and mathematical operations.
    
    Evaluate mathematical expressions with support for basic arithmetic,
    trigonometric functions, logarithms, and mathematical constants.
    """
    pass


@calc_group.command(name="evaluate")
@click.argument("expression")
@click.option("--precision", "-p", default=6, help="Number of decimal places")
def evaluate_expression(expression, precision):
    """
    Evaluate a mathematical expression.
    
    Supports: +, -, *, /, **, (), sin, cos, tan, log, ln, sqrt, pi, e
    Example: mtool util calc evaluate "2 + 2 * 3"
    """
    try:
        # Define safe mathematical functions and constants
        safe_dict = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': math.log10,
            'ln': math.log,
            'sqrt': math.sqrt,
            'abs': abs,
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil,
            'pi': math.pi,
            'e': math.e,
            'inf': float('inf'),
            'nan': float('nan')
        }
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        # Format output
        if isinstance(result, (int, float)):
            if result == int(result):
                click.echo(f"Result: {int(result)}")
            else:
                click.echo(f"Result: {result:.{precision}f}")
        else:
            click.echo(f"Result: {result}")
            
    except ZeroDivisionError:
        click.echo("Error: Division by zero", err=True)
    except ValueError as e:
        click.echo(f"Error: Invalid mathematical operation - {e}", err=True)
    except SyntaxError:
        click.echo("Error: Invalid expression syntax", err=True)
    except Exception as e:
        click.echo(f"Error evaluating expression: {e}", err=True)


@click.group(name="convert")
def convert_group():
    """
    Unit conversion tools.
    
    Convert between various units including length, weight, temperature,
    area, volume, speed, and more with automatic unit detection.
    """
    pass


# Unit conversion dictionaries
LENGTH_UNITS = {
    'm': 1.0, 'meter': 1.0, 'meters': 1.0,
    'km': 1000.0, 'kilometer': 1000.0, 'kilometers': 1000.0,
    'cm': 0.01, 'centimeter': 0.01, 'centimeters': 0.01,
    'mm': 0.001, 'millimeter': 0.001, 'millimeters': 0.001,
    'mi': 1609.344, 'mile': 1609.344, 'miles': 1609.344,
    'yd': 0.9144, 'yard': 0.9144, 'yards': 0.9144,
    'ft': 0.3048, 'foot': 0.3048, 'feet': 0.3048,
    'in': 0.0254, 'inch': 0.0254, 'inches': 0.0254,
    'nm': 1e-9, 'nanometer': 1e-9, 'nanometers': 1e-9,
    'µm': 1e-6, 'micrometer': 1e-6, 'micrometers': 1e-6,
    'au': 149597870700.0, 'astronomical_unit': 149597870700.0,
    'ly': 9.461e15, 'light_year': 9.461e15, 'light_years': 9.461e15
}

WEIGHT_UNITS = {
    'kg': 1.0, 'kilogram': 1.0, 'kilograms': 1.0,
    'g': 0.001, 'gram': 0.001, 'grams': 0.001,
    'mg': 1e-6, 'milligram': 1e-6, 'milligrams': 1e-6,
    'lb': 0.45359237, 'pound': 0.45359237, 'pounds': 0.45359237,
    'oz': 0.028349523125, 'ounce': 0.028349523125, 'ounces': 0.028349523125,
    'ton': 1000.0, 'metric_ton': 1000.0, 'metric_tons': 1000.0,
    'st': 6.35029318, 'stone': 6.35029318, 'stones': 6.35029318
}

TEMPERATURE_UNITS = {
    'c': 'celsius', 'celsius': 'celsius',
    'f': 'fahrenheit', 'fahrenheit': 'fahrenheit',
    'k': 'kelvin', 'kelvin': 'kelvin'
}

AREA_UNITS = {
    'm²': 1.0, 'sq_m': 1.0, 'square_meter': 1.0, 'square_meters': 1.0,
    'km²': 1e6, 'sq_km': 1e6, 'square_kilometer': 1e6, 'square_kilometers': 1e6,
    'cm²': 1e-4, 'sq_cm': 1e-4, 'square_centimeter': 1e-4, 'square_centimeters': 1e-4,
    'mm²': 1e-6, 'sq_mm': 1e-6, 'square_millimeter': 1e-6, 'square_millimeters': 1e-6,
    'mi²': 2589988.110336, 'sq_mi': 2589988.110336, 'square_mile': 2589988.110336, 'square_miles': 2589988.110336,
    'ac': 4046.8564224, 'acre': 4046.8564224, 'acres': 4046.8564224,
    'ha': 10000.0, 'hectare': 10000.0, 'hectares': 10000.0
}

VOLUME_UNITS = {
    'l': 1.0, 'liter': 1.0, 'liters': 1.0,
    'ml': 0.001, 'milliliter': 0.001, 'milliliters': 0.001,
    'cl': 0.01, 'centiliter': 0.01, 'centiliters': 0.01,
    'dl': 0.1, 'deciliter': 0.1, 'deciliters': 0.1,
    'gal': 3.785411784, 'gallon': 3.785411784, 'gallons': 3.785411784,
    'qt': 0.946352946, 'quart': 0.946352946, 'quarts': 0.946352946,
    'pt': 0.473176473, 'pint': 0.473176473, 'pints': 0.473176473,
    'cup': 0.236588236, 'cups': 0.236588236,
    'fl_oz': 0.0295735295625, 'fluid_ounce': 0.0295735295625, 'fluid_ounces': 0.0295735295625,
    'm³': 1000.0, 'cubic_meter': 1000.0, 'cubic_meters': 1000.0,
    'cm³': 0.001, 'cubic_centimeter': 0.001, 'cubic_centimeters': 0.001
}

SPEED_UNITS = {
    'm/s': 1.0, 'meter_per_second': 1.0, 'meters_per_second': 1.0,
    'km/h': 0.277777778, 'kilometer_per_hour': 0.277777778, 'kilometers_per_hour': 0.277777778,
    'mph': 0.44704, 'mile_per_hour': 0.44704, 'miles_per_hour': 0.44704,
    'knot': 0.514444444, 'knots': 0.514444444,
    'ft/s': 0.3048, 'foot_per_second': 0.3048, 'feet_per_second': 0.3048
}


def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

def celsius_to_kelvin(celsius):
    return celsius + 273.15

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def fahrenheit_to_kelvin(fahrenheit):
    return celsius_to_kelvin(fahrenheit_to_celsius(fahrenheit))

def kelvin_to_fahrenheit(kelvin):
    return celsius_to_fahrenheit(kelvin_to_celsius(kelvin))


@convert_group.command(name="unit")
@click.argument("conversion")
@click.option("--precision", "-p", default=6, help="Number of decimal places")
def convert_unit(conversion, precision):
    """
    Convert between different units.
    
    Examples:
    mtool util convert unit "10 km to mi"
    mtool util convert unit "32 f to c"
    mtool util convert unit "100 kg to lb"
    """
    try:
        # Parse the conversion string
        # Pattern: <value> <from_unit> to <to_unit>
        pattern = r'^(\d+(?:\.\d+)?)\s+([^\s]+)\s+to\s+([^\s]+)$'
        match = re.match(pattern, conversion.lower())
        
        if not match:
            click.echo("Error: Invalid format. Use: <value> <from_unit> to <to_unit>", err=True)
            click.echo("Examples: '10 km to mi', '32 f to c', '100 kg to lb'", err=True)
            return
        
        value, from_unit, to_unit = match.groups()
        value = float(value)
        
        # Determine unit type and convert
        result = None
        
        # Temperature conversion
        if from_unit in TEMPERATURE_UNITS and to_unit in TEMPERATURE_UNITS:
            from_temp = TEMPERATURE_UNITS[from_unit]
            to_temp = TEMPERATURE_UNITS[to_unit]
            
            # Convert to Celsius first
            if from_temp == 'celsius':
                celsius = value
            elif from_temp == 'fahrenheit':
                celsius = fahrenheit_to_celsius(value)
            elif from_temp == 'kelvin':
                celsius = kelvin_to_celsius(value)
            
            # Convert from Celsius to target unit
            if to_temp == 'celsius':
                result = celsius
            elif to_temp == 'fahrenheit':
                result = celsius_to_fahrenheit(celsius)
            elif to_temp == 'kelvin':
                result = celsius_to_kelvin(celsius)
        
        # Length conversion
        elif from_unit in LENGTH_UNITS and to_unit in LENGTH_UNITS:
            meters = value * LENGTH_UNITS[from_unit]
            result = meters / LENGTH_UNITS[to_unit]
        
        # Weight conversion
        elif from_unit in WEIGHT_UNITS and to_unit in WEIGHT_UNITS:
            kg = value * WEIGHT_UNITS[from_unit]
            result = kg / WEIGHT_UNITS[to_unit]
        
        # Area conversion
        elif from_unit in AREA_UNITS and to_unit in AREA_UNITS:
            sq_meters = value * AREA_UNITS[from_unit]
            result = sq_meters / AREA_UNITS[to_unit]
        
        # Volume conversion
        elif from_unit in VOLUME_UNITS and to_unit in VOLUME_UNITS:
            liters = value * VOLUME_UNITS[from_unit]
            result = liters / VOLUME_UNITS[to_unit]
        
        # Speed conversion
        elif from_unit in SPEED_UNITS and to_unit in SPEED_UNITS:
            mps = value * SPEED_UNITS[from_unit]
            result = mps / SPEED_UNITS[to_unit]
        
        else:
            click.echo(f"Error: Unsupported unit conversion from '{from_unit}' to '{to_unit}'", err=True)
            return
        
        # Format output
        if result == int(result):
            click.echo(f"{value} {from_unit} = {int(result)} {to_unit}")
        else:
            click.echo(f"{value} {from_unit} = {result:.{precision}f} {to_unit}")
            
    except ValueError:
        click.echo("Error: Invalid numeric value", err=True)
    except Exception as e:
        click.echo(f"Error converting units: {e}", err=True)


@click.group(name="encode")
def encode_group():
    """
    Computer science encoding and decoding tools.
    
    Convert between different data representations including base64, hex,
    binary, URL encoding, and Church encoding for lambda calculus.
    """
    pass


@encode_group.command(name="base64")
@click.argument("operation", type=click.Choice(['encode', 'decode']))
@click.argument("text")
def base64_operation(operation, text):
    """
    Encode or decode text using Base64.
    
    Examples:
    mtool util encode base64 encode "Hello World"
    mtool util encode base64 decode "SGVsbG8gV29ybGQ="
    """
    try:
        if operation == 'encode':
            # Encode text to base64
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            click.echo(f"Encoded: {encoded}")
        else:
            # Decode base64 to text
            decoded = base64.b64decode(text.encode('utf-8')).decode('utf-8')
            click.echo(f"Decoded: {decoded}")
            
    except Exception as e:
        click.echo(f"Error in base64 operation: {e}", err=True)


@encode_group.command(name="hex")
@click.argument("operation", type=click.Choice(['encode', 'decode']))
@click.argument("text")
def hex_operation(operation, text):
    """
    Encode or decode text using hexadecimal.
    
    Examples:
    mtool util encode hex encode "Hello"
    mtool util encode hex decode "48656c6c6f"
    """
    try:
        if operation == 'encode':
            # Encode text to hex
            encoded = text.encode('utf-8').hex()
            click.echo(f"Encoded: {encoded}")
        else:
            # Decode hex to text
            decoded = bytes.fromhex(text).decode('utf-8')
            click.echo(f"Decoded: {decoded}")
            
    except Exception as e:
        click.echo(f"Error in hex operation: {e}", err=True)


@encode_group.command(name="binary")
@click.argument("operation", type=click.Choice(['encode', 'decode']))
@click.argument("text")
def binary_operation(operation, text):
    """
    Encode or decode text using binary representation.
    
    Examples:
    mtool util encode binary encode "Hi"
    mtool util encode binary decode "1001000 1101001"
    """
    try:
        if operation == 'encode':
            # Encode text to binary
            binary = ' '.join(format(ord(char), '08b') for char in text)
            click.echo(f"Encoded: {binary}")
        else:
            # Decode binary to text
            # Remove spaces and split into 8-bit chunks
            binary_clean = text.replace(' ', '')
            if len(binary_clean) % 8 != 0:
                click.echo("Error: Invalid binary string length", err=True)
                return
            
            # Convert each 8-bit chunk to character
            decoded = ''
            for i in range(0, len(binary_clean), 8):
                byte = binary_clean[i:i+8]
                char_code = int(byte, 2)
                decoded += chr(char_code)
            
            click.echo(f"Decoded: {decoded}")
            
    except Exception as e:
        click.echo(f"Error in binary operation: {e}", err=True)


@encode_group.command(name="url")
@click.argument("operation", type=click.Choice(['encode', 'decode']))
@click.argument("text")
def url_operation(operation, text):
    """
    URL encode or decode text.
    
    Examples:
    mtool util encode url encode "Hello World!"
    mtool util encode url decode "Hello%20World%21"
    """
    try:
        import urllib.parse
        
        if operation == 'encode':
            # URL encode text
            encoded = urllib.parse.quote(text)
            click.echo(f"Encoded: {encoded}")
        else:
            # URL decode text
            decoded = urllib.parse.unquote(text)
            click.echo(f"Decoded: {decoded}")
            
    except Exception as e:
        click.echo(f"Error in URL operation: {e}", err=True)


@encode_group.command(name="church")
@click.argument("number", type=int)
@click.option("--show-lambda", "-l", is_flag=True, help="Show lambda calculus notation")
def church_encoding(number, show_lambda):
    """
    Convert a number to Church encoding (lambda calculus representation).
    
    Church numerals represent numbers as functions that apply another function n times.
    Example: mtool util encode church 3
    """
    try:
        if number < 0:
            click.echo("Error: Church encoding only supports non-negative integers", err=True)
            return
        
        if number == 0:
            church_num = "λf.λx.x"
            description = "Zero: function that returns x without applying f"
        else:
            # Generate Church numeral: λf.λx.f(f(...f(x)...)) with n applications of f
            church_num = f"λf.λx.{'f(' * number}x{')' * number}"
            description = f"Number {number}: function that applies f {number} times to x"
        
        click.echo(f"Church encoding of {number}:")
        click.echo(f"  {church_num}")
        click.echo(f"  {description}")
        
        if show_lambda:
            # Show the mathematical notation
            if number == 0:
                lambda_notation = "0 = λf.λx.x"
            else:
                lambda_notation = f"{number} = λf.λx.f^{number}(x)"
            click.echo(f"  Mathematical: {lambda_notation}")
        
        # Show example usage
        click.echo(f"\nExample usage:")
        click.echo(f"  If f = λx.x+1 and x = 0, then:")
        click.echo(f"  {church_num}(λx.x+1)(0) = {number}")
        
    except Exception as e:
        click.echo(f"Error in Church encoding: {e}", err=True)


# Register all groups
calc_group.add_command(evaluate_expression)
convert_group.add_command(convert_unit)
encode_group.add_command(base64_operation)
encode_group.add_command(hex_operation)
encode_group.add_command(binary_operation)
encode_group.add_command(url_operation)
encode_group.add_command(church_encoding) 