"""
Command argument parser setup and configuration.
"""

import argparse

def setup_argparse():
    """Set up the argument parser with comprehensive command structure."""
    parser = argparse.ArgumentParser(
        description="Browser Agent - Control your browser with natural language commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🔍 COMMANDS:
  run         Run the browser agent (default command)
  launch      Launch Chrome with debugging enabled
  connect     Connect to existing Chrome debug instance
  profiles    Manage browser profiles
  diagnose    Run system diagnostics
  clean       Clean up temporary files and profiles
  config      View and manage configuration
  version     Show version and system information
  help        Show detailed help for commands

🌐 PROFILE OPTIONS:
  --profile temp       Use temporary clean profile (no saved information)
  --profile default    Use default browser profile (with saved logins, bookmarks, history)

⚙️ MODE OPTIONS (when Chrome is already running):
  --mode close_reopen  Close Chrome and reopen with debugging (clean profile)
  --mode new_window    Open new Chrome window with debugging (clean session)

📝 EXAMPLES:
  # Start with clean browser session
  uv run main.py run --profile temp
  
  # Start with default browser profile (saved logins, bookmarks, etc.)
  uv run main.py run --profile default
  
  # Launch Chrome with debugging enabled
  uv run main.py launch --profile temp --mode close_reopen
  
  # Connect to existing Chrome debug instance
  uv run main.py connect --port 9222
  
  # Run system diagnostics
  uv run main.py diagnose
  
  # Clean up temporary files
  uv run main.py clean --temp-profiles
  
  # View current configuration
  uv run main.py config --show

💡 PROFILE MANAGEMENT:
  Use 'uv run main.py profiles --list' to see all available profiles.
  Use 'uv run main.py profiles --clean' to remove old profiles.
  
  Note: Replace 'uv run' with 'python' if using pip instead of uv.
        """
    )
    
    # Global options
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-essential output")
    parser.add_argument("--no-banner", action="store_true", help="Don't show the banner")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # 'run' command (default)
    run_parser = subparsers.add_parser("run", help="Run the browser agent")
    run_parser.add_argument("--task", "-t", type=str, help="Initial task to execute")
    run_parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    run_parser.add_argument("--profile", choices=["temp", "default"], default="temp",
                           help="Browser profile: 'temp' (clean) or 'default' (local browser with saved data)")
    run_parser.add_argument("--mode", choices=["close_reopen", "new_window"], 
                           help="If Chrome is running: 'close_reopen' (keep logins) or 'new_window' (clean)")
    run_parser.add_argument("--port", type=int, default=9222, help="Debug port (default: 9222)")
    run_parser.add_argument("--timeout", type=int, default=30, help="Connection timeout in seconds")
    run_parser.add_argument("--max-retries", type=int, default=3, help="Maximum connection retries")
    
    # 'launch' command
    launch_parser = subparsers.add_parser("launch", help="Launch Chrome browser with debugging enabled")
    launch_parser.add_argument("--port", "-p", type=int, default=9222, help="Debug port (default: 9222)")
    launch_parser.add_argument("--profile", choices=["temp", "default"], default="temp",
                             help="Browser profile: 'temp' (clean) or 'default' (local browser with saved data)")
    launch_parser.add_argument("--mode", "-m", choices=["close_reopen", "new_window"], 
                             help="If Chrome is running: 'close_reopen' (keep logins) or 'new_window' (clean)")
    launch_parser.add_argument("--wait", action="store_true", help="Wait for Chrome to be ready before exiting")
    launch_parser.add_argument("--background", action="store_true", help="Launch Chrome in background")
    
    # 'connect' command
    connect_parser = subparsers.add_parser("connect", help="Connect to existing Chrome debug instance")
    connect_parser.add_argument("--port", "-p", type=int, default=9222, help="Debug port (default: 9222)")
    connect_parser.add_argument("--host", default="localhost", help="Debug host (default: localhost)")
    connect_parser.add_argument("--timeout", type=int, default=10, help="Connection timeout in seconds")
    connect_parser.add_argument("--test-only", action="store_true", help="Only test connection, don't start agent")
    
    # 'profiles' command
    profiles_parser = subparsers.add_parser("profiles", help="Manage browser profiles")
    profiles_group = profiles_parser.add_mutually_exclusive_group()
    profiles_group.add_argument("--list", action="store_true", help="List all available profiles")
    profiles_group.add_argument("--clean", action="store_true", help="Clean up old profiles")
    profiles_group.add_argument("--create", type=str, help="Create a new profile with given name")
    profiles_group.add_argument("--remove", type=str, help="Remove a profile by name")
    profiles_group.add_argument("--info", type=str, help="Show information about a profile")
    profiles_parser.add_argument("--force", action="store_true", help="Force operations without confirmation")
    
    # 'diagnose' command
    diagnose_parser = subparsers.add_parser("diagnose", help="Run system diagnostics")
    diagnose_parser.add_argument("--full", action="store_true", help="Run full diagnostic suite")
    diagnose_parser.add_argument("--chrome", action="store_true", help="Check Chrome installation and processes")
    diagnose_parser.add_argument("--deps", action="store_true", help="Check Python dependencies")
    diagnose_parser.add_argument("--config", action="store_true", help="Check configuration")
    diagnose_parser.add_argument("--network", action="store_true", help="Test network connectivity")
    diagnose_parser.add_argument("--export", type=str, help="Export diagnostic report to file")
    
    # 'clean' command
    clean_parser = subparsers.add_parser("clean", help="Clean up temporary files and profiles")
    clean_parser.add_argument("--temp-profiles", action="store_true", help="Remove temporary profiles")
    clean_parser.add_argument("--cache", action="store_true", help="Clear browser cache")
    clean_parser.add_argument("--logs", action="store_true", help="Remove log files")
    clean_parser.add_argument("--all", action="store_true", help="Clean everything")
    clean_parser.add_argument("--force", action="store_true", help="Force cleanup without confirmation")
    clean_parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without doing it")
    
    # 'config' command
    config_parser = subparsers.add_parser("config", help="View and manage configuration")
    config_group = config_parser.add_mutually_exclusive_group()
    config_group.add_argument("--show", action="store_true", help="Show current configuration")
    config_group.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set configuration value")
    config_group.add_argument("--get", type=str, help="Get configuration value")
    config_group.add_argument("--reset", action="store_true", help="Reset configuration to defaults")
    config_parser.add_argument("--export", type=str, help="Export configuration to file")
    config_parser.add_argument("--import", type=str, help="Import configuration from file")
    
    # 'debug' command
    debug_parser = subparsers.add_parser("debug", help="Run in debug mode with verbose logging")
    debug_parser.add_argument("--task", "-t", type=str, help="Initial task to execute")
    debug_parser.add_argument("--profile", choices=["temp", "default"], default="temp",
                             help="Browser profile to use")
    debug_parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                             default="DEBUG", help="Log level")
    debug_parser.add_argument("--log-file", type=str, help="Log to file instead of console")
    
    # 'version' command
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.add_argument("--json", action="store_true", help="Output version info as JSON")
    version_parser.add_argument("--check-updates", action="store_true", help="Check for available updates")
    version_parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    
    # 'help' command
    help_parser = subparsers.add_parser("help", help="Show detailed help for commands")
    help_parser.add_argument("topic", nargs="?", help="Help topic (command name)")
    
    return parser
