#!/usr/bin/env python3
"""
Example usage of mtool
"""

import subprocess
import tempfile
import os
from pathlib import Path

def create_test_files():
    """Create some test files for demonstration"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create a test text file
    with open(test_dir / "test.txt", "w") as f:
        f.write("This is a test file for mtool demonstration.\n" * 100)
    
    # Create a simple test image (if PIL is available)
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), "Test Image", fill='black')
        img.save(test_dir / "test.png")
        print("Created test image: test_files/test.png")
    except ImportError:
        print("PIL not available, skipping image creation")
    
    print("Created test files in test_files/ directory")
    return test_dir

def run_example_commands():
    """Run example mtool commands"""
    examples = [
        # File compression examples
        ["mtool", "file", "compress", "zip", "test_files", "test_files.zip"],
        ["mtool", "file", "compress", "gzip", "test_files/test.txt", "test_files/test.txt.gz"],
        
        # File extraction examples
        ["mtool", "file", "extract", "zip", "test_files.zip", "extracted_zip"],
        ["mtool", "file", "extract", "gzip", "test_files/test.txt.gz", "extracted_text.txt"],
        
        # File conversion examples (if test image exists)
        ["mtool", "file", "convert", "image", "test_files/test.png", "test_files/test.jpg", "--quality", "85"],
    ]
    
    print("Running example commands...")
    print()
    
    for cmd in examples:
        print(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Success")
            else:
                print(f"✗ Failed: {result.stderr}")
        except FileNotFoundError:
            print("✗ Command not found")
        print()

def main():
    print("mtool Examples")
    print("=" * 50)
    print()
    
    # Check if mtool is installed
    try:
        result = subprocess.run(['mtool', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("mtool not found. Please install with: pip install -e .")
            return
    except FileNotFoundError:
        print("mtool not found. Please install with: pip install -e .")
        return
    
    print("✓ mtool is installed")
    print()
    
    # Create test files
    test_dir = create_test_files()
    print()
    
    # Run examples
    run_example_commands()
    
    print("Example completed!")
    print("\nYou can now try these commands manually:")
    print("  mtool file compress zip test_files test_files.zip")
    print("  mtool file extract zip test_files.zip extracted")
    print("  mtool file convert image test_files/test.png test_files/test.jpg")

if __name__ == "__main__":
    main() 