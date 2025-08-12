"""
Status and progress reporting utilities.
"""

import sys
from datetime import datetime
from .colors import Colors, colorize

def print_status_bar(message: str, status: str = "INFO"):
    """Print a formatted status message with proper cursor handling and colors."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    status_config = {
        "INFO": {"icon": "ℹ️", "color": Colors.BRIGHT_BLUE},
        "SUCCESS": {"icon": "✅", "color": Colors.BRIGHT_GREEN},
        "WARNING": {"icon": "⚠️", "color": Colors.BRIGHT_YELLOW},
        "ERROR": {"icon": "❌", "color": Colors.BRIGHT_RED},
        "PROGRESS": {"icon": "🔄", "color": Colors.BRIGHT_CYAN}
    }
    
    config = status_config.get(status, status_config["INFO"])
    icon = config["icon"]
    color = config["color"]
    
    # Ensure clean line printing with colors
    timestamp_colored = colorize(f"[{timestamp}]", Colors.BRIGHT_BLACK)
    message_colored = colorize(message, color)
    
    sys.stdout.write(f"\r\033[K{timestamp_colored} {icon} {message_colored}\n")
    sys.stdout.flush()

def print_section_header(title: str):
    """Print a formatted section header with colors."""
    separator = "="*60
    print(f"\n{Colors.BRIGHT_CYAN}{separator}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{separator}{Colors.RESET}")
