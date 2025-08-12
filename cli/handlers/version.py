"""
Version command implementation.
"""

import json
from cli.core import print_colored, print_status_bar, Colors
from cli.utils import get_system_info, check_dependencies

def command_version(args):
    """Show version information with colors."""
    if not args.json:
        print_colored("Detailed Information:", Colors.BRIGHT_CYAN, Colors.BOLD)
        info = get_system_info()
        print_colored(f"  - Version: {info['version']}", Colors.BRIGHT_GREEN)
        print_colored(f"  - Python: {info['python_version']}", Colors.BRIGHT_BLUE)
        print_colored(f"  - Platform: {info['platform']}", Colors.BRIGHT_MAGENTA)
        print_colored(f"  - Current directory: {info['current_directory']}", Colors.BRIGHT_CYAN)
        print_colored(f"  - Chrome processes: {info['chrome_processes']}", Colors.BRIGHT_YELLOW)
        
        api_configured = 'Yes' if info['api_key_configured'] else 'No'
        api_color = Colors.BRIGHT_GREEN if info['api_key_configured'] else Colors.BRIGHT_RED
        print_colored(f"  - API key configured: {api_configured}", api_color)
        
        print_colored("\nDependencies:", Colors.BRIGHT_CYAN, Colors.BOLD)
        deps = check_dependencies()
        for dep, version in deps.items():
            if "❌" in str(version):
                print_colored(f"  - {dep}: {version}", Colors.BRIGHT_RED)
            else:
                print_colored(f"  - {dep}: {version}", Colors.BRIGHT_GREEN)
        
        if args.check_updates:
            print_colored("\n🔍 Checking for updates...", Colors.BRIGHT_YELLOW)
            print_status_bar("Update checking not yet implemented", "WARNING")
    else:
        # JSON output
        info = get_system_info()
        info['dependencies'] = check_dependencies()
        print(json.dumps(info, indent=2))
    
    return True
