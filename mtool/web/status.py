"""
Web status checking tools
"""

import click
import requests
import socket
import time
from urllib.parse import urlparse


@click.group(name="status")
def status_group():
    """
    Network connectivity and service status monitoring tools.
    
    Check if websites are online and responding with status codes and response times.
    Test port connectivity on hosts. Ping hosts to verify network reachability.
    Monitor website status over time with configurable intervals. Check SSL certificate
    information including validity dates and issuer details.
    """
    pass


@status_group.command(name="check")
@click.argument("url")
@click.option("--timeout", default=10, help="Timeout in seconds")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def check_status(url, timeout, verbose):
    """
    Check if a website is online and responding.
    """
    try:
        # Ensure URL has scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        start_time = time.time()
        
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        response_time = time.time() - start_time
        
        status_code = response.status_code
        status_text = response.reason
        
        if status_code < 400:
            click.echo(f"✅ {url} is ONLINE")
            click.echo(f"Status: {status_code} {status_text}")
            click.echo(f"Response Time: {response_time:.2f}s")
            
            if verbose:
                click.echo(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
                click.echo(f"Content-Length: {response.headers.get('content-length', 'Unknown')}")
                click.echo(f"Server: {response.headers.get('server', 'Unknown')}")
                
        elif status_code < 500:
            click.echo(f"⚠️  {url} is ONLINE but has client error")
            click.echo(f"Status: {status_code} {status_text}")
            click.echo(f"Response Time: {response_time:.2f}s")
        else:
            click.echo(f"❌ {url} is ONLINE but has server error")
            click.echo(f"Status: {status_code} {status_text}")
            click.echo(f"Response Time: {response_time:.2f}s")
            
    except requests.ConnectionError:
        click.echo(f"❌ {url} is OFFLINE (Connection failed)")
    except requests.Timeout:
        click.echo(f"❌ {url} is OFFLINE (Request timed out)")
    except requests.RequestException as e:
        click.echo(f"❌ {url} is OFFLINE ({e})")
    except Exception as e:
        click.echo(f"Error checking status: {e}", err=True)


@status_group.command(name="port")
@click.argument("host")
@click.argument("port", type=int)
@click.option("--timeout", default=5, help="Timeout in seconds")
def check_port(host, port, timeout):
    """
    Check if a port is open on a host.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            click.echo(f"✅ Port {port} is OPEN on {host}")
        else:
            click.echo(f"❌ Port {port} is CLOSED on {host}")
            
    except socket.gaierror:
        click.echo(f"❌ Could not resolve hostname: {host}", err=True)
    except Exception as e:
        click.echo(f"Error checking port: {e}", err=True)


@status_group.command(name="ping")
@click.argument("host")
@click.option("--count", default=4, help="Number of pings to send")
@click.option("--timeout", default=5, help="Timeout in seconds")
def ping_host(host, count, timeout):
    """
    Ping a host to check connectivity.
    """
    try:
        import subprocess
        import platform
        
        # Determine ping command based on OS
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
        else:
            cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo(f"✅ {host} is reachable")
            click.echo(result.stdout)
        else:
            click.echo(f"❌ {host} is not reachable")
            if result.stderr:
                click.echo(result.stderr)
                
    except FileNotFoundError:
        click.echo("Error: ping command not found", err=True)
    except Exception as e:
        click.echo(f"Error pinging host: {e}", err=True)


@status_group.command(name="monitor")
@click.argument("url")
@click.option("--interval", default=30, help="Check interval in seconds")
@click.option("--count", default=10, help="Number of checks to perform")
def monitor_status(url, interval, count):
    """
    Monitor a website's status over time.
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        click.echo(f"Monitoring {url} every {interval} seconds for {count} checks...")
        click.echo("-" * 50)
        
        for i in range(count):
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10, allow_redirects=True)
                response_time = time.time() - start_time
                
                timestamp = time.strftime("%H:%M:%S")
                status = "✅" if response.status_code < 400 else "❌"
                
                click.echo(f"[{timestamp}] {status} {response.status_code} - {response_time:.2f}s")
                
            except requests.RequestException as e:
                timestamp = time.strftime("%H:%M:%S")
                click.echo(f"[{timestamp}] ❌ Error - {e}")
            
            if i < count - 1:  # Don't sleep after the last check
                time.sleep(interval)
                
    except KeyboardInterrupt:
        click.echo("\nMonitoring stopped by user")
    except Exception as e:
        click.echo(f"Error monitoring status: {e}", err=True)


@status_group.command(name="ssl")
@click.argument("url")
def check_ssl(url):
    """
    Check SSL certificate information for a website.
    """
    try:
        import ssl
        import socket
        
        # Ensure URL has scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        hostname = parsed.netloc
        port = parsed.port or 443
        
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                click.echo(f"SSL Certificate for {hostname}:")
                click.echo(f"Subject: {cert.get('subject', 'Unknown')}")
                click.echo(f"Issuer: {cert.get('issuer', 'Unknown')}")
                click.echo(f"Version: {cert.get('version', 'Unknown')}")
                click.echo(f"Serial Number: {cert.get('serialNumber', 'Unknown')}")
                
                # Parse dates
                not_before = cert.get('notBefore', 'Unknown')
                not_after = cert.get('notAfter', 'Unknown')
                
                click.echo(f"Valid From: {not_before}")
                click.echo(f"Valid Until: {not_after}")
                
                # Check if certificate is valid
                import datetime
                now = datetime.datetime.now()
                
                try:
                    from dateutil import parser
                    valid_from = parser.parse(not_before)
                    valid_until = parser.parse(not_after)
                    
                    if valid_from <= now <= valid_until:
                        click.echo("✅ Certificate is valid")
                    else:
                        click.echo("❌ Certificate is not valid")
                        
                except ImportError:
                    click.echo("Note: Install python-dateutil for date validation")
                    
    except ssl.SSLError as e:
        click.echo(f"❌ SSL Error: {e}", err=True)
    except socket.gaierror:
        click.echo(f"❌ Could not resolve hostname: {hostname}", err=True)
    except Exception as e:
        click.echo(f"Error checking SSL: {e}", err=True) 