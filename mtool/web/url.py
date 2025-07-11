"""
URL utility tools
"""

import click
import requests
import urllib.parse
from urllib.parse import urlparse
import json


@click.group(name="url")
def url_group():
    """
    URL manipulation and analysis tools.
    
    Get detailed URL information (scheme, domain, path, headers, redirects).
    Validate URL format and accessibility. Shorten URLs using services (TinyURL, is.gd).
    Expand shortened URLs to original URLs. Encode and decode URL-safe text.
    """
    pass


@url_group.command(name="info")
@click.argument("url")
def url_info(url):
    """
    Get detailed information about a URL.
    """
    try:
        # Parse URL
        parsed = urlparse(url)
        
        click.echo(f"URL: {url}")
        click.echo(f"Scheme: {parsed.scheme}")
        click.echo(f"Domain: {parsed.netloc}")
        click.echo(f"Path: {parsed.path}")
        click.echo(f"Query: {parsed.query}")
        click.echo(f"Fragment: {parsed.fragment}")
        
        # Try to get HTTP headers
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            click.echo(f"\nHTTP Status: {response.status_code}")
            click.echo(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
            click.echo(f"Content-Length: {response.headers.get('content-length', 'Unknown')}")
            click.echo(f"Server: {response.headers.get('server', 'Unknown')}")
            
            if response.history:
                click.echo(f"Redirects: {len(response.history)}")
                for i, resp in enumerate(response.history, 1):
                    click.echo(f"  {i}. {resp.url}")
                    
        except requests.RequestException as e:
            click.echo(f"\nCould not fetch URL: {e}")
            
    except Exception as e:
        click.echo(f"Error analyzing URL: {e}", err=True)


@url_group.command(name="validate")
@click.argument("url")
def validate_url(url):
    """
    Validate if a URL is properly formatted and accessible.
    """
    try:
        # Check URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            click.echo("❌ Invalid URL format", err=True)
            return
        
        click.echo("✅ URL format is valid")
        
        # Check if accessible
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code < 400:
                click.echo(f"✅ URL is accessible (Status: {response.status_code})")
            else:
                click.echo(f"⚠️  URL returned error status: {response.status_code}", err=True)
                
        except requests.ConnectionError:
            click.echo("❌ Connection failed - URL may not exist", err=True)
        except requests.Timeout:
            click.echo("❌ Request timed out", err=True)
        except requests.RequestException as e:
            click.echo(f"❌ Request failed: {e}", err=True)
            
    except Exception as e:
        click.echo(f"Error validating URL: {e}", err=True)


@url_group.command(name="shorten")
@click.argument("url")
@click.option("--service", default="tinyurl", type=click.Choice(['tinyurl', 'isgd']), 
              help="URL shortening service to use")
def shorten_url(url, service):
    """
    Shorten a URL using a URL shortening service.
    """
    try:
        # Validate URL first
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            click.echo("Error: Invalid URL format", err=True)
            return
        
        if service == "tinyurl":
            api_url = "http://tinyurl.com/api-create.php"
            params = {"url": url}
        elif service == "isgd":
            api_url = "https://is.gd/create.php"
            params = {"format": "json", "url": url}
        
        response = requests.get(api_url, params=params, timeout=10)
        
        if response.status_code == 200:
            if service == "isgd":
                try:
                    data = response.json()
                    if data.get("errorcode"):
                        click.echo(f"Error: {data.get('errormessage', 'Unknown error')}", err=True)
                        return
                    shortened = data.get("shorturl")
                except json.JSONDecodeError:
                    click.echo("Error: Invalid response from service", err=True)
                    return
            else:
                shortened = response.text.strip()
            
            click.echo(f"Original: {url}")
            click.echo(f"Shortened: {shortened}")
        else:
            click.echo(f"Error: Service returned status {response.status_code}", err=True)
            
    except requests.RequestException as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error shortening URL: {e}", err=True)


@url_group.command(name="expand")
@click.argument("short_url")
def expand_url(short_url):
    """
    Expand a shortened URL to show the original URL.
    """
    try:
        response = requests.head(short_url, timeout=10, allow_redirects=True)
        
        if response.history:
            original_url = response.history[-1].url
            click.echo(f"Short URL: {short_url}")
            click.echo(f"Original URL: {original_url}")
            
            if len(response.history) > 1:
                click.echo(f"Redirects: {len(response.history)}")
        else:
            click.echo("No redirects found - URL may not be shortened")
            
    except requests.RequestException as e:
        click.echo(f"Error expanding URL: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@url_group.command(name="encode")
@click.argument("text")
def encode_url(text):
    """
    URL encode text for use in URLs.
    """
    try:
        encoded = urllib.parse.quote(text)
        click.echo(f"Original: {text}")
        click.echo(f"Encoded: {encoded}")
    except Exception as e:
        click.echo(f"Error encoding text: {e}", err=True)


@url_group.command(name="decode")
@click.argument("encoded_text")
def decode_url(encoded_text):
    """
    URL decode text from URLs.
    """
    try:
        decoded = urllib.parse.unquote(encoded_text)
        click.echo(f"Encoded: {encoded_text}")
        click.echo(f"Decoded: {decoded}")
    except Exception as e:
        click.echo(f"Error decoding text: {e}", err=True) 