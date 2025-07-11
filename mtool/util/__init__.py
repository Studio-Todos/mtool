"""
Utility tools for mtool
"""

import click
from mtool.util.qrcodegen import qrcode_group
from mtool.util.calc import calc_group, convert_group, encode_group

@click.group(name="util")
def util_group():
    """
    System utility tools.
    
    Generate QR codes from text or URLs with ASCII art display in terminal
    and optional PNG file output. Perform mathematical calculations and unit
    conversions. Encode and decode data in various formats including Church
    encoding for lambda calculus.
    """
    pass

util_group.add_command(qrcode_group)
util_group.add_command(calc_group)
util_group.add_command(convert_group)
util_group.add_command(encode_group) 