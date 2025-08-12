"""
Launch command implementation.
"""

import time
import urllib.request
from cli.core import print_status_bar, colorize, Colors

def command_launch(args):
    """Launch Chrome with debugging enabled."""
    from cli.chrome_launcher import launch_chrome_with_debugging
    
    port = args.port
    use_default_profile = (args.profile == "default")  # Use default profile if specified
    mode = getattr(args, 'mode', None)
    
    profile_desc = "default browser profile (with saved data)" if use_default_profile else "clean temporary profile"
    
    print_status_bar(f"Launching Chrome with debugging on port {port} ({profile_desc})...", "PROGRESS")
    
    success = launch_chrome_with_debugging(
        port=port, 
        use_default_profile=use_default_profile,
        mode=mode
    )
    
    if success:
        print_status_bar(f"Chrome launched successfully on port {port}", "SUCCESS")
        if use_default_profile:
            print_status_bar("Using default profile - your saved logins and bookmarks are available", "INFO")
        else:
            print_status_bar("Using temporary profile - no login information", "INFO")
        print(f"🔗 CDP endpoint: {colorize(f'http://localhost:{port}', Colors.BRIGHT_CYAN, Colors.UNDERLINE)}")
        
        if args.wait:
            print_status_bar("Waiting for Chrome to be ready...", "PROGRESS")
            time.sleep(3)
            if test_chrome_connection(port):
                print_status_bar("Chrome is ready for connections", "SUCCESS")
            else:
                print_status_bar("Chrome may not be fully ready", "WARNING")
        
        print(f"\n💡 You can now run the Browser Agent with:")
        print(f"   {colorize(f'uv run main.py run --port {port}', Colors.BRIGHT_GREEN)}")
        print(f"   {colorize(f'# Or: python main.py run --port {port}', Colors.BRIGHT_BLACK)}")
    else:
        print_status_bar("Failed to launch Chrome with debugging", "ERROR")
        return False
    
    return True

def test_chrome_connection(port: int, host: str = "localhost", timeout: int = 10) -> bool:
    """Test if Chrome debug port is accessible."""
    try:
        url = f"http://{host}:{port}/json/version"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read()
            return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return False
