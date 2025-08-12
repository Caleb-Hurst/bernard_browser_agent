"""
Connect command implementation.
"""

from argparse import Namespace
from cli.core import print_status_bar, print_colored, colorize, Colors
from .launch import test_chrome_connection

def command_connect(args):
    """Connect to existing Chrome debug instance."""
    port = args.port
    host = args.host
    
    print_status_bar(f"Testing connection to {host}:{port}...", "PROGRESS")
    
    if test_chrome_connection(port, host, args.timeout):
        print_status_bar("Connection successful!", "SUCCESS")
        
        if not args.test_only:
            print_status_bar("Starting Browser Agent...", "PROGRESS")
            # Create a mock args object for command_run
            from .run import command_run
            run_args = Namespace(
                command="run",
                task=None,
                headless=False,
                profile="temp",
                mode=None,
                port=port,
                timeout=args.timeout,
                max_retries=3,
                verbose=False
            )
            return command_run(run_args)
        return True
    else:
        print_status_bar("Connection failed!", "ERROR")
        print_colored(f"💡 Make sure Chrome is running with debugging enabled on port {port}", Colors.BRIGHT_YELLOW)
        print(f"   You can launch it with: {colorize(f'uv run main.py launch --port {port}', Colors.BRIGHT_GREEN)}")
        print(f"   {colorize(f'# Or: python main.py launch --port {port}', Colors.BRIGHT_BLACK)}")
        return False
