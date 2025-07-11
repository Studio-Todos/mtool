"""
Web download tools
"""

import click
import requests
import os
from pathlib import Path
from urllib.parse import urlparse
import time


@click.group(name="download")
def download_group():
    """
    Web file download utilities with advanced features.
    
    Download single files with progress tracking and resume capabilities.
    Download multiple files in batch operations. Download images with format
    validation and metadata extraction. Check file availability and download
    status before downloading.
    """
    pass


@download_group.command(name="file")
@click.argument("url")
@click.argument("output", type=click.Path(), default=".")
@click.option("--timeout", default=30, help="Timeout in seconds")
@click.option("--progress", is_flag=True, help="Show download progress")
def download_file(url, output, timeout, progress):
    """
    Download a file from a URL.
    """
    try:
        # Parse URL to get filename if output is directory
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename:
            filename = "downloaded_file"
        
        # Determine output path
        if os.path.isdir(output) or output == ".":
            output_path = Path(output) / filename
        else:
            output_path = Path(output)
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"Downloading {url} to {output_path}")
        
        # Download with progress
        if progress:
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            click.echo(f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)", nl=False)
                        else:
                            click.echo(f"\rDownloaded: {downloaded} bytes", nl=False)
            
            click.echo()  # New line after progress
            
        else:
            # Simple download without progress
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
        
        file_size = output_path.stat().st_size
        click.echo(f"✅ Download completed: {file_size} bytes")
        
    except requests.RequestException as e:
        click.echo(f"❌ Download failed: {e}", err=True)
    except Exception as e:
        click.echo(f"Error downloading file: {e}", err=True)


@download_group.command(name="batch")
@click.argument("urls", nargs=-1)
@click.argument("output_dir", type=click.Path(), default=".")
@click.option("--timeout", default=30, help="Timeout in seconds")
def download_batch(urls, output_dir, timeout):
    """
    Download multiple files from URLs.
    """
    if not urls:
        click.echo("Error: No URLs provided", err=True)
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls, 1):
        try:
            click.echo(f"[{i}/{len(urls)}] Downloading {url}")
            
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            if not filename:
                filename = f"downloaded_file_{i}"
            
            file_path = output_path / filename
            
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            file_size = file_path.stat().st_size
            click.echo(f"✅ Downloaded: {filename} ({file_size} bytes)")
            successful += 1
            
        except requests.RequestException as e:
            click.echo(f"❌ Failed: {url} - {e}", err=True)
            failed += 1
        except Exception as e:
            click.echo(f"❌ Error: {url} - {e}", err=True)
            failed += 1
    
    click.echo(f"\nDownload Summary: {successful} successful, {failed} failed")


@download_group.command(name="image")
@click.argument("url")
@click.argument("output", type=click.Path(), default=".")
@click.option("--timeout", default=30, help="Timeout in seconds")
def download_image(url, output, timeout):
    """
    Download an image from a URL with validation.
    """
    try:
        # Parse URL to get filename
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename or not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
            filename = "downloaded_image.jpg"
        
        # Determine output path
        if os.path.isdir(output) or output == ".":
            output_path = Path(output) / filename
        else:
            output_path = Path(output)
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"Downloading image from {url}")
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Check if it's actually an image
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            click.echo(f"⚠️  Warning: Content-Type is {content_type}, not an image", err=True)
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        file_size = output_path.stat().st_size
        click.echo(f"✅ Image downloaded: {file_size} bytes")
        
        # Try to get image info
        try:
            from PIL import Image
            with Image.open(output_path) as img:
                width, height = img.size
                format_name = img.format
                click.echo(f"Image info: {width}x{height} pixels, format: {format_name}")
        except ImportError:
            click.echo("Install Pillow for image information")
        except Exception:
            pass  # Ignore image info errors
        
    except requests.RequestException as e:
        click.echo(f"❌ Download failed: {e}", err=True)
    except Exception as e:
        click.echo(f"Error downloading image: {e}", err=True)


@download_group.command(name="check")
@click.argument("url")
@click.option("--timeout", default=10, help="Timeout in seconds")
def check_download(url, timeout):
    """
    Check if a file can be downloaded without actually downloading it.
    """
    try:
        click.echo(f"Checking download availability for {url}")
        
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        content_length = response.headers.get('content-length')
        content_type = response.headers.get('content-type', 'Unknown')
        
        click.echo(f"✅ File is available for download")
        click.echo(f"Content-Type: {content_type}")
        
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            click.echo(f"File Size: {size_mb:.2f} MB ({content_length} bytes)")
        else:
            click.echo("File Size: Unknown")
        
        # Check if filename can be determined
        parsed_url = urlparse(response.url)
        filename = os.path.basename(parsed_url.path)
        
        if filename:
            click.echo(f"Suggested filename: {filename}")
        else:
            click.echo("No filename in URL")
            
    except requests.RequestException as e:
        click.echo(f"❌ File not available: {e}", err=True)
    except Exception as e:
        click.echo(f"Error checking download: {e}", err=True)


@download_group.command(name="resume")
@click.argument("url")
@click.argument("output", type=click.Path())
@click.option("--timeout", default=30, help="Timeout in seconds")
def resume_download(url, output, timeout):
    """
    Resume a partially downloaded file.
    """
    try:
        output_path = Path(output)
        
        if not output_path.exists():
            click.echo("File doesn't exist. Starting new download...")
            download_file.callback(url, str(output_path), timeout, False)
            return
        
        # Get file size
        current_size = output_path.stat().st_size
        
        click.echo(f"Resuming download from {current_size} bytes")
        
        # Set range header for resume
        headers = {'Range': f'bytes={current_size}-'}
        
        response = requests.get(url, headers=headers, stream=True, timeout=timeout)
        
        if response.status_code == 206:  # Partial content
            total_size = int(response.headers.get('content-range', '').split('/')[-1])
            remaining = total_size - current_size
            
            click.echo(f"Remaining to download: {remaining} bytes")
            
            with open(output_path, 'ab') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            click.echo("✅ Download resumed successfully")
            
        elif response.status_code == 200:
            click.echo("Server doesn't support resume. Starting fresh download...")
            download_file.callback(url, str(output_path), timeout, False)
        else:
            click.echo(f"❌ Resume failed: HTTP {response.status_code}", err=True)
            
    except requests.RequestException as e:
        click.echo(f"❌ Resume failed: {e}", err=True)
    except Exception as e:
        click.echo(f"Error resuming download: {e}", err=True) 