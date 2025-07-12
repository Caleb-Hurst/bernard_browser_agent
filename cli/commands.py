"""
Command-line interface for Browser Agent.
Comprehensive CLI with full-featured commands, diagnostics, and profile management.
"""

import os
import sys
import argparse
import json
import time
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cli.chrome_launcher import launch_chrome_with_debugging
from configurations.config import BROWSER_OPTIONS, BROWSER_CONNECTION, LLM_PROVIDER, CURRENT_LLM_CONFIG

# ANSI Color Codes
class Colors:
    """ANSI color codes for terminal output."""
    # Reset
    RESET = '\033[0m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'

def colorize(text: str, color: str = "", style: str = "") -> str:
    """Apply color and style to text."""
    # Check environment variables for color control
    if os.environ.get('NO_COLOR') or not sys.stdout.isatty():
        return text
    return f"{style}{color}{text}{Colors.RESET}"

def print_colored(text: str, color: str = "", style: str = "", end: str = "\n"):
    """Print colored text."""
    print(colorize(text, color, style), end=end)

def get_version():
    return "1.0.0"

def get_system_info():
    """Get system information for diagnostics."""
    return {
        "version": get_version(),
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "current_directory": os.getcwd(),
        "chrome_processes": count_chrome_processes(),
        "debug_profiles": list_debug_profiles(),
        "temp_profiles": list_temp_profiles(),
        "api_key_configured": bool(CURRENT_LLM_CONFIG.get("api_key")),
        "browser_options": BROWSER_OPTIONS,
        "connection_config": BROWSER_CONNECTION
    }

def count_chrome_processes():
    """Count running Chrome processes."""
    try:
        if sys.platform == "darwin":  # macOS
            result = subprocess.run(["pgrep", "-c", "Chrome"], capture_output=True, text=True)
            return int(result.stdout.strip()) if result.returncode == 0 else 0
        elif sys.platform == "linux":
            result = subprocess.run(["pgrep", "-c", "chrome"], capture_output=True, text=True)
            return int(result.stdout.strip()) if result.returncode == 0 else 0
        else:  # Windows
            result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq chrome.exe"], capture_output=True, text=True)
            return len([line for line in result.stdout.split('\n') if 'chrome.exe' in line])
    except:
        return 0

def list_debug_profiles():
    """List available debug profiles."""
    profiles = []
    if sys.platform == "darwin":
        debug_dir = Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Debug"
    elif sys.platform == "linux":
        debug_dir = Path.home() / ".config" / "google-chrome" / "Debug"
    else:
        debug_dir = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Debug"
    
    if debug_dir.exists():
        for item in debug_dir.iterdir():
            if item.is_dir():
                profiles.append(str(item))
    return profiles

def list_temp_profiles():
    """List temporary profiles in system temp directory."""
    temp_dir = Path(tempfile.gettempdir())
    temp_profiles = []
    for item in temp_dir.glob("chrome_temp_*"):
        if item.is_dir():
            temp_profiles.append(str(item))
    return temp_profiles

def check_dependencies():
    """Check if required dependencies are installed."""
    deps = {}
    
    try:
        import playwright
        deps["playwright"] = getattr(playwright, '__version__', 'unknown')
    except ImportError:
        deps["playwright"] = "❌ Not installed"
    
    try:
        import langchain
        deps["langchain"] = getattr(langchain, '__version__', 'unknown')
    except ImportError:
        deps["langchain"] = "❌ Not installed"
    
    try:
        import openai
        deps["openai"] = getattr(openai, '__version__', 'unknown')
    except ImportError:
        deps["openai"] = "❌ Not installed"
    
    try:
        import groq
        deps["groq"] = getattr(groq, '__version__', 'unknown')
    except ImportError:
        deps["groq"] = "❌ Not installed"
    
    return deps

def print_banner():
    banner = f"""
{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BRIGHT_CYAN}║{Colors.RESET}                      {Colors.BRIGHT_BLUE}🌐 Browser Agent 🌐{Colors.RESET}                     {Colors.BRIGHT_CYAN}║{Colors.RESET}
{Colors.BRIGHT_CYAN}║{Colors.RESET}                        {Colors.BRIGHT_GREEN}Version {get_version()}{Colors.RESET}                         {Colors.BRIGHT_CYAN}║{Colors.RESET}
{Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
    {Colors.CYAN}An AI agent that controls your browser through natural language{Colors.RESET}
    """
    print(banner)

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

def validate_environment():
    """Validate that the environment is properly configured."""
    issues = []
    
    if not CURRENT_LLM_CONFIG.get("api_key"):
        issues.append(f"{LLM_PROVIDER.upper()} API key is not configured (set {LLM_PROVIDER.upper()}_API_KEY environment variable)")
    
    deps = check_dependencies()
    for dep, version in deps.items():
        if "❌" in str(version):
            issues.append(f"Missing dependency: {dep}")
    
    return issues

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

def command_run(args):
    """Execute the main browser agent with enhanced error handling and status reporting."""
    from browser.browser_setup import initialize_browser, close_browser
    from browser.controllers.browser_controller import initialize
    from agent.agent import create_agent
    
    print_status_bar("Starting Browser Agent...", "PROGRESS")
    
    # Validate environment first
    issues = validate_environment()
    if issues:
        print_status_bar("Environment validation failed:", "ERROR")
        for issue in issues:
            print(f"  • {issue}")
        return False
    
    # Configure browser options
    if hasattr(args, 'headless') and args.headless:
        BROWSER_OPTIONS["headless"] = True
        print_status_bar("Running in headless mode", "INFO")
    
    # Create the agent with enhanced error handling
    print_status_bar("Creating AI agent with tools...", "PROGRESS")
    try:
        agent_executor = create_agent()
        print_status_bar("Agent created successfully!", "SUCCESS")
    except Exception as agent_error:
        print_status_bar(f"Failed to create agent: {str(agent_error)}", "ERROR")
        if args.verbose:
            import traceback
            print("\nDetailed traceback:")
            traceback.print_exc()
        return False

    # Handle Chrome launching with enhanced options
    if BROWSER_CONNECTION.get("use_existing", False):
        port = getattr(args, 'port', 9222)
        if "cdp_endpoint" in BROWSER_CONNECTION:
            try:
                endpoint = BROWSER_CONNECTION["cdp_endpoint"]
                port = int(endpoint.split(":")[-1])
            except (ValueError, IndexError):
                pass
        
        print_status_bar(f"Connecting to Chrome debug port {port}...", "PROGRESS")
        
        # Determine profile and mode settings
        use_default_profile = (args.profile == "default")  # Use default profile if specified
        launch_mode = getattr(args, 'mode', None)
        
        # Enhanced Chrome launching with timeout and retries
        max_retries = getattr(args, 'max_retries', 3)
        timeout = getattr(args, 'timeout', 30)
        
        for attempt in range(max_retries):
            print_status_bar(f"Chrome launch attempt {attempt + 1}/{max_retries}...", "PROGRESS")
            
            chrome_launched = launch_chrome_with_debugging(
                port=port, 
                use_default_profile=use_default_profile,
                mode=launch_mode
            )
            
            if chrome_launched:
                print_status_bar("Chrome launched successfully!", "SUCCESS")
                break
            elif attempt < max_retries - 1:
                print_status_bar(f"Chrome launch failed, retrying in 1 second...", "WARNING")
                time.sleep(1)  # Reduced retry delay
            else:
                print_status_bar("All Chrome launch attempts failed", "ERROR")
                if not BROWSER_CONNECTION.get("fallback_to_new", True):
                    print_status_bar("Fallback to new browser is disabled", "ERROR")
                    return False
    
    # Initialize browser with enhanced error handling
    print_status_bar("Initializing browser connection...", "PROGRESS")
    try:
        playwright, browser, page = initialize_browser(BROWSER_OPTIONS, BROWSER_CONNECTION)
        print_status_bar("Browser initialized successfully!", "SUCCESS")
    except Exception as e:
        print_status_bar(f"Failed to initialize browser: {str(e)}", "ERROR")
        return False

    using_connected_browser = BROWSER_CONNECTION.get("use_existing", False)
    
    print_status_bar("Setting up browser controller...", "PROGRESS")
    try:
        initialize(page)
        print_status_bar("Browser controller ready!", "SUCCESS")
    except Exception as e:
        print_status_bar(f"Failed to initialize browser controller: {str(e)}", "ERROR")
        return False
    
    # Handle initial task if provided
    if hasattr(args, 'task') and args.task:
        print_section_header(f"Executing Initial Task: {args.task}")
        start_time = datetime.now()
        
        try:
            response = agent_executor.invoke(args.task)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print_status_bar(f"Task completed in {duration:.2f} seconds", "SUCCESS")
            print("\n" + "="*60)
            print("TASK RESULT:")
            print("="*60)
            print(response.get("output", "No output received"))
            print("="*60)
        except Exception as e:
            print_status_bar(f"Task execution failed: {str(e)}", "ERROR")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    # Interactive mode with enhanced prompts
    print_section_header("Interactive Mode")
    print_colored("💬 Enter your instructions for the browser agent", Colors.BRIGHT_GREEN)
    print_colored("💡 Type 'help' for available commands or 'exit' to quit", Colors.BRIGHT_YELLOW)
    print_colored("🔍 Use 'status' to check system status", Colors.BRIGHT_BLUE)
    
    # Setup terminal for better experience
    terminal_ready = setup_terminal()
    if terminal_ready:
        print_status_bar("Terminal enhanced with history and completion", "INFO")
    
    interaction_count = 0
    keep_running = True
    
    while keep_running:
        try:
            # Clear any pending output and reset cursor
            reset_cursor()
            
            # Create a clean prompt with proper formatting and colors
            prompt_prefix = colorize(f"[{interaction_count}]", Colors.BRIGHT_BLACK)
            prompt_text = colorize("Browser Agent", Colors.BRIGHT_CYAN, Colors.BOLD)
            prompt_symbol = colorize("> ", Colors.BRIGHT_WHITE)
            prompt = f"\n{prompt_prefix} {prompt_text}{prompt_symbol}"
            
            try:
                # Use input() with proper cursor management
                user_query = input(prompt).strip()
            except EOFError:
                # Handle Ctrl+D gracefully
                print("\n")
                print_status_bar("Input stream closed", "INFO")
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C in the input prompt
                print("\n")
                print_status_bar("Interrupted", "WARNING")
                try:
                    confirm = input("Are you sure you want to exit? (y/N): ")
                    if confirm.lower() in ['y', 'yes']:
                        break
                    else:
                        continue
                except (EOFError, KeyboardInterrupt):
                    print("\nForced exit")
                    break
            
            if not user_query:
                continue
            
            # Handle special commands
            if user_query.lower() in ['exit', 'quit', 'q']:
                print_status_bar("Goodbye! 👋", "INFO")
                break
            elif user_query.lower() == 'help':
                print_interactive_help()
                continue
            elif user_query.lower() == 'status':
                print_system_status()
                continue
            elif user_query.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            
            interaction_count += 1
            print_status_bar(f"Processing instruction: {user_query}", "PROGRESS")
            start_time = datetime.now()
            
            try:
                response = agent_executor.invoke(user_query)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print_status_bar(f"Execution completed in {duration:.2f} seconds", "SUCCESS")
                print_agent_response(response.get("output", "No output received"))
                    
            except Exception as e:
                print_status_bar(f"Execution error: {str(e)}", "ERROR")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                print_colored("💡 The agent encountered an error but the browser will remain open.", Colors.BRIGHT_YELLOW)
                print_colored("   You can continue with a new instruction.", Colors.BRIGHT_YELLOW)
                
        except Exception as unexpected_error:
            print_status_bar(f"Unexpected error in interactive loop: {str(unexpected_error)}", "ERROR")
            if args.verbose:
                import traceback
                traceback.print_exc()
            print("💡 An unexpected error occurred. You can try again or exit.")
    
    # Enhanced cleanup with options
    print_section_header("Cleanup")
    if 'playwright' in locals() and 'browser' in locals():
        if using_connected_browser:
            close_input = input("Disconnect from browser? (y/N): ")
        else:
            close_input = input("Close browser? (y/N): ")
            
        if close_input.lower() in ['y', 'yes']:
            print_status_bar("Cleaning up browser resources...", "PROGRESS")
            try:
                close_browser(playwright, browser, is_connected=using_connected_browser)
                print_status_bar("Browser cleanup completed", "SUCCESS")
            except Exception as e:
                print_status_bar(f"Cleanup warning: {str(e)}", "WARNING")
        else:
            print_status_bar("Browser left open for manual control", "INFO")
    
    return True

def print_interactive_help():
    """Print help for interactive mode with colors."""
    print(f"""
{Colors.BRIGHT_CYAN}🔧 INTERACTIVE COMMANDS:{Colors.RESET}
  {Colors.BRIGHT_GREEN}help{Colors.RESET}     Show this help message
  {Colors.BRIGHT_GREEN}status{Colors.RESET}   Show system status
  {Colors.BRIGHT_GREEN}clear{Colors.RESET}    Clear the screen
  {Colors.BRIGHT_RED}exit{Colors.RESET}     Exit the Browser Agent
  {Colors.BRIGHT_RED}quit{Colors.RESET}     Exit the Browser Agent
  {Colors.BRIGHT_RED}q{Colors.RESET}        Exit the Browser Agent

{Colors.BRIGHT_YELLOW}💡 TIPS:{Colors.RESET}
  - Be specific about what you want the browser to do
  - Use natural language: {Colors.BRIGHT_WHITE}"Go to Google and search for Python"{Colors.RESET}
  - The agent can handle complex multi-step tasks
  - Use {Colors.BRIGHT_MAGENTA}Ctrl+C{Colors.RESET} to interrupt long-running tasks
    """)

def print_system_status():
    """Print current system status with colors."""
    print_section_header("System Status")
    info = get_system_info()
    
    print_colored(f"🔧 Version: {info['version']}", Colors.BRIGHT_GREEN)
    print_colored(f"🐍 Python: {info['python_version']}", Colors.BRIGHT_BLUE)
    print_colored(f"🖥️  Platform: {info['platform']}", Colors.BRIGHT_CYAN)
    print_colored(f"🌐 Chrome Processes: {info['chrome_processes']}", Colors.BRIGHT_YELLOW)
    
    api_status = "✅ Configured" if info['api_key_configured'] else "❌ Missing"
    api_color = Colors.BRIGHT_GREEN if info['api_key_configured'] else Colors.BRIGHT_RED
    print_colored(f"🔑 API Key: {api_status}", api_color)
    
    print_colored(f"📁 Debug Profiles: {len(info['debug_profiles'])}", Colors.BRIGHT_MAGENTA)
    print_colored(f"🗂️  Temp Profiles: {len(info['temp_profiles'])}", Colors.BRIGHT_CYAN)
    
    if info['chrome_processes'] > 0:
        print_colored("✅ Chrome is running", Colors.BRIGHT_GREEN)
    else:
        print_colored("⚠️  Chrome is not running", Colors.BRIGHT_YELLOW)

def command_launch(args):
    """Launch Chrome with debugging enabled."""
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
            from argparse import Namespace
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

def command_profiles(args):
    """Manage browser profiles."""
    print_section_header("Profile Management")
    
    if args.list:
        print("🔍 Available Profiles:")
        debug_profiles = list_debug_profiles()
        temp_profiles = list_temp_profiles()
        
        print(f"\n📁 Debug Profiles ({len(debug_profiles)}):")
        for i, profile in enumerate(debug_profiles, 1):
            print(f"  {i}. {profile}")
        
        print(f"\n🗂️  Temporary Profiles ({len(temp_profiles)}):")
        for i, profile in enumerate(temp_profiles, 1):
            print(f"  {i}. {profile}")
        
        if not debug_profiles and not temp_profiles:
            print("  No profiles found")
    
    elif args.clean:
        print("🧹 Cleaning up old profiles...")
        temp_profiles = list_temp_profiles()
        
        if not temp_profiles:
            print_status_bar("No temporary profiles to clean", "INFO")
            return True
        
        print(f"Found {len(temp_profiles)} temporary profiles to clean:")
        for profile in temp_profiles:
            print(f"  • {profile}")
        
        if not args.force:
            confirm = input("\nProceed with cleanup? (y/N): ")
            if confirm.lower() not in ['y', 'yes']:
                print_status_bar("Cleanup cancelled", "INFO")
                return True
        
        cleaned = 0
        for profile in temp_profiles:
            try:
                shutil.rmtree(profile)
                cleaned += 1
                print_status_bar(f"Removed: {profile}", "SUCCESS")
            except Exception as e:
                print_status_bar(f"Failed to remove {profile}: {str(e)}", "ERROR")
        
        print_status_bar(f"Cleaned up {cleaned}/{len(temp_profiles)} profiles", "SUCCESS")
    
    elif args.create:
        print(f"📝 Creating new profile: {args.create}")
        # Profile creation logic would go here
        print_status_bar("Profile creation not yet implemented", "WARNING")
    
    elif args.remove:
        print(f"🗑️  Removing profile: {args.remove}")
        # Profile removal logic would go here
        print_status_bar("Profile removal not yet implemented", "WARNING")
    
    elif args.info:
        print(f"ℹ️  Profile information: {args.info}")
        # Profile info logic would go here
        print_status_bar("Profile info not yet implemented", "WARNING")
    
    else:
        print("💡 Use --list to see available profiles")
        print("   Use --clean to remove temporary profiles")
    
    return True

def command_diagnose(args):
    """Run system diagnostics."""
    print_section_header("System Diagnostics")
    
    if args.full or not any([args.chrome, args.deps, args.config, args.network]):
        # Run all diagnostics
        run_all_diagnostics()
    else:
        if args.chrome:
            diagnose_chrome()
        if args.deps:
            diagnose_dependencies()
        if args.config:
            diagnose_configuration()
        if args.network:
            diagnose_network()
    
    if args.export:
        export_diagnostic_report(args.export)
    
    return True

def command_clean(args):
    """Clean up temporary files and profiles."""
    print_section_header("Cleanup Operations")
    
    if args.all:
        args.temp_profiles = True
        args.cache = True
        args.logs = True
    
    operations = []
    if args.temp_profiles:
        operations.append("temporary profiles")
    if args.cache:
        operations.append("browser cache")
    if args.logs:
        operations.append("log files")
    
    if not operations:
        print_status_bar("No cleanup operations specified", "WARNING")
        print("💡 Use --temp-profiles, --cache, --logs, or --all")
        return True
    
    print(f"🧹 Cleanup operations: {', '.join(operations)}")
    
    if args.dry_run:
        print_status_bar("DRY RUN - No files will be actually removed", "INFO")
    
    if not args.force and not args.dry_run:
        confirm = input("\nProceed with cleanup? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print_status_bar("Cleanup cancelled", "INFO")
            return True
    
    success = True
    
    if args.temp_profiles:
        success &= cleanup_temp_profiles(args.dry_run)
    
    if args.cache:
        success &= cleanup_cache(args.dry_run)
    
    if args.logs:
        success &= cleanup_logs(args.dry_run)
    
    if success:
        print_status_bar("Cleanup completed successfully", "SUCCESS")
    else:
        print_status_bar("Cleanup completed with some errors", "WARNING")
    
    return success

def command_config(args):
    """View and manage configuration."""
    print_section_header("Configuration Management")
    
    if args.show:
        show_configuration()
    elif args.set:
        key, value = args.set
        set_configuration(key, value)
    elif args.get:
        get_configuration(args.get)
    elif args.reset:
        reset_configuration()
    elif args.export:
        export_configuration(args.export)
    elif getattr(args, 'import', None):
        import_configuration(getattr(args, 'import'))
    else:
        show_configuration()
    
    return True

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

def command_help(args):
    """Show detailed help for commands."""
    if args.topic:
        show_command_help(args.topic)
    else:
        show_general_help()
    return True

def command_debug(args):
    """Run in debug mode with verbose logging."""
    print_status_bar("Starting DEBUG mode with verbose logging", "INFO")
    
    import logging
    log_level = getattr(logging, args.log_level)
    
    if args.log_file:
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=args.log_file
        )
        print_status_bar(f"Logging to file: {args.log_file}", "INFO")
    else:
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Create a mock args object for command_run
    from argparse import Namespace
    run_args = Namespace(
        command="run",
        task=args.task,
        headless=False,
        profile="temp",
        mode=None,
        port=9222,
        timeout=30,
        max_retries=3,
        verbose=True
    )
    
    return command_run(run_args)

# Helper functions for command implementations

def test_chrome_connection(port: int, host: str = "localhost", timeout: int = 10) -> bool:
    """Test if Chrome debug port is accessible."""
    import urllib.request
    import urllib.error
    
    try:
        url = f"http://{host}:{port}/json/version"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read()
            return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return False

def run_all_diagnostics():
    """Run complete diagnostic suite."""
    print_status_bar("Running comprehensive diagnostics...", "PROGRESS")
    
    diagnose_chrome()
    diagnose_dependencies()
    diagnose_configuration()
    diagnose_network()
    
    print_status_bar("Diagnostics complete", "SUCCESS")

def diagnose_chrome():
    """Diagnose Chrome installation and processes with colors."""
    print(f"\n{Colors.BRIGHT_BLUE}🌐 Chrome Diagnostics:{Colors.RESET}")
    
    # Check Chrome processes
    chrome_count = count_chrome_processes()
    print_colored(f"  • Running Chrome processes: {chrome_count}", Colors.BRIGHT_CYAN)
    
    # Check for Chrome executable
    chrome_paths = []
    if sys.platform == "darwin":
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
        ]
    elif sys.platform == "linux":
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium"
        ]
    else:  # Windows
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print_colored(f"  • Chrome executable found: {path}", Colors.BRIGHT_GREEN)
            chrome_found = True
            break
    
    if not chrome_found:
        print_colored("  • ⚠️  Chrome executable not found in standard locations", Colors.BRIGHT_YELLOW)
    
    # Test debug port
    if test_chrome_connection(9222):
        print_colored("  • ✅ Debug port 9222 accessible", Colors.BRIGHT_GREEN)
    else:
        print_colored("  • ❌ Debug port 9222 not accessible", Colors.BRIGHT_RED)

def diagnose_dependencies():
    """Diagnose Python dependencies with colors."""
    print(f"\n{Colors.BRIGHT_BLUE}🐍 Python Dependencies:{Colors.RESET}")
    
    deps = check_dependencies()
    for dep, version in deps.items():
        if "❌" in str(version):
            print_colored(f"  • ❌ {dep}: Not installed", Colors.BRIGHT_RED)
        else:
            print_colored(f"  • ✅ {dep}: {version}", Colors.BRIGHT_GREEN)

def diagnose_configuration():
    """Diagnose configuration issues with colors."""
    print(f"\n{Colors.BRIGHT_BLUE}⚙️  Configuration:{Colors.RESET}")
    
    # Check API key
    if CURRENT_LLM_CONFIG.get("api_key"):
        print_colored("  • ✅ OpenAI API key configured", Colors.BRIGHT_GREEN)
    else:
        print_colored("  • ❌ OpenAI API key not configured", Colors.BRIGHT_RED)
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print_colored("  • ✅ .env file found", Colors.BRIGHT_GREEN)
    else:
        print_colored("  • ⚠️  .env file not found", Colors.BRIGHT_YELLOW)
    
    # Check browser options
    headless_status = BROWSER_OPTIONS.get('headless', False)
    headless_color = Colors.BRIGHT_YELLOW if headless_status else Colors.BRIGHT_GREEN
    print_colored(f"  • Browser headless: {headless_status}", headless_color)
    
    channel = BROWSER_OPTIONS.get('channel', 'unknown')
    print_colored(f"  • Browser channel: {channel}", Colors.BRIGHT_CYAN)
    
    connection_mode = 'Existing' if BROWSER_CONNECTION.get('use_existing') else 'New'
    connection_color = Colors.BRIGHT_MAGENTA if connection_mode == 'Existing' else Colors.BRIGHT_BLUE
    print_colored(f"  • Connection mode: {connection_mode}", connection_color)

def diagnose_network():
    """Diagnose network connectivity with colors."""
    print(f"\n{Colors.BRIGHT_BLUE}🌐 Network Connectivity:{Colors.RESET}")
    
    # Test localhost connection
    if test_chrome_connection(9222):
        print_colored("  • ✅ localhost:9222 accessible", Colors.BRIGHT_GREEN)
    else:
        print_colored("  • ❌ localhost:9222 not accessible", Colors.BRIGHT_RED)
    
    # Test internet connectivity
    import urllib.request
    try:
        with urllib.request.urlopen("https://www.google.com", timeout=5):
            print_colored("  • ✅ Internet connectivity available", Colors.BRIGHT_GREEN)
    except:
        print_colored("  • ❌ Internet connectivity issues", Colors.BRIGHT_RED)

def export_diagnostic_report(filename: str):
    """Export diagnostic report to file."""
    print_status_bar(f"Exporting diagnostic report to {filename}...", "PROGRESS")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info(),
        "dependencies": check_dependencies(),
        "chrome_processes": count_chrome_processes(),
        "debug_port_accessible": test_chrome_connection(9222),
        "profiles": {
            "debug": list_debug_profiles(),
            "temp": list_temp_profiles()
        }
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print_status_bar(f"Report exported successfully", "SUCCESS")
    except Exception as e:
        print_status_bar(f"Failed to export report: {str(e)}", "ERROR")

def cleanup_temp_profiles(dry_run: bool = False) -> bool:
    """Clean up temporary profiles."""
    print_status_bar("Cleaning temporary profiles...", "PROGRESS")
    
    temp_profiles = list_temp_profiles()
    if not temp_profiles:
        print_status_bar("No temporary profiles to clean", "INFO")
        return True
    
    success = True
    for profile in temp_profiles:
        try:
            if dry_run:
                print(f"  Would remove: {profile}")
            else:
                shutil.rmtree(profile)
                print(f"  Removed: {profile}")
        except Exception as e:
            print_status_bar(f"Failed to remove {profile}: {str(e)}", "ERROR")
            success = False
    
    return success

def cleanup_cache(dry_run: bool = False) -> bool:
    """Clean up browser cache."""
    print_status_bar("Cleaning browser cache...", "PROGRESS")
    
    if dry_run:
        print("  Would clear browser cache files")
    else:
        print_status_bar("Cache cleanup not yet implemented", "WARNING")
    
    return True

def cleanup_logs(dry_run: bool = False) -> bool:
    """Clean up log files."""
    print_status_bar("Cleaning log files...", "PROGRESS")
    
    if dry_run:
        print("  Would remove log files")
    else:
        print_status_bar("Log cleanup not yet implemented", "WARNING")
    
    return True

def show_configuration():
    """Show current configuration with colors."""
    print_colored("📋 Current Configuration:", Colors.BRIGHT_CYAN, Colors.BOLD)
    
    api_status = "✅ Set" if CURRENT_LLM_CONFIG.get("api_key") else "❌ Not set"
    api_color = Colors.BRIGHT_GREEN if CURRENT_LLM_CONFIG.get("api_key") else Colors.BRIGHT_RED
    
    config = {
        f"{LLM_PROVIDER.upper()} API Key": (api_status, api_color),
        "LLM Provider": (LLM_PROVIDER.upper(), Colors.BRIGHT_BLUE),
        "Model": (CURRENT_LLM_CONFIG.get("model", "Unknown"), Colors.BRIGHT_MAGENTA),
        "Browser Options": (None, None),  # Special handling for dict
        "Connection Settings": (None, None),  # Special handling for dict
    }
    
    for key, (value, color) in config.items():
        if key in ["Browser Options", "Connection Settings"]:
            print_colored(f"  {key}:", Colors.BRIGHT_YELLOW)
            data = BROWSER_OPTIONS if key == "Browser Options" else BROWSER_CONNECTION
            for sub_key, sub_value in data.items():
                print_colored(f"    {sub_key}: {sub_value}", Colors.WHITE)
        else:
            print_colored(f"  {key}: ", Colors.BRIGHT_WHITE, end="")
            print_colored(value, color)

def set_configuration(key: str, value: str):
    """Set configuration value."""
    print_status_bar(f"Setting {key} = {value}", "INFO")
    print_status_bar("Configuration setting not yet implemented", "WARNING")

def get_configuration(key: str):
    """Get configuration value."""
    print_status_bar(f"Getting configuration for: {key}", "INFO")
    print_status_bar("Configuration getting not yet implemented", "WARNING")

def reset_configuration():
    """Reset configuration to defaults."""
    print_status_bar("Resetting configuration to defaults...", "PROGRESS")
    print_status_bar("Configuration reset not yet implemented", "WARNING")

def export_configuration(filename: str):
    """Export configuration to file."""
    print_status_bar(f"Exporting configuration to {filename}...", "PROGRESS")
    
    config = {
        "browser_options": BROWSER_OPTIONS,
        "connection_settings": BROWSER_CONNECTION,
        "version": get_version(),
        "export_timestamp": datetime.now().isoformat()
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print_status_bar("Configuration exported successfully", "SUCCESS")
    except Exception as e:
        print_status_bar(f"Failed to export configuration: {str(e)}", "ERROR")

def import_configuration(filename: str):
    """Import configuration from file."""
    print_status_bar(f"Importing configuration from {filename}...", "PROGRESS")
    print_status_bar("Configuration import not yet implemented", "WARNING")

def show_command_help(topic: str):
    """Show detailed help for a specific command."""
    help_topics = {
        "run": """
🚀 RUN COMMAND:
  Launch and control the browser agent with natural language commands.
  
  Usage: uv run main.py run [options]
  
  Options:
    --task, -t        Initial task to execute
    --headless        Run in headless mode
    --profile         Browser profile (temp, default)
    --mode           Launch mode (close_reopen, new_window)
    --port           Debug port (default: 9222)
    --timeout        Connection timeout in seconds
    --max-retries    Maximum connection retries
  
  Examples:
    uv run main.py run --task "Go to Google"
    uv run main.py run --profile temp --headless
    uv run main.py run --profile default --task "Check my Gmail"
    
  Note: Replace 'uv run' with 'python' if using pip instead of uv.
        """,
        "launch": """
🔧 LAUNCH COMMAND:
  Launch Chrome with debugging enabled.
  
  Usage: uv run main.py launch [options]
  
  Options:
    --port, -p       Debug port (default: 9222)
    --profile        Browser profile (temp, default)
    --mode, -m       Launch mode (close_reopen, new_window)
    --wait           Wait for Chrome to be ready
    --background     Launch in background
  
  Examples:
    uv run main.py launch --port 9223
    uv run main.py launch --profile temp --wait
    uv run main.py launch --profile default --mode close_reopen
    
  Note: Replace 'uv run' with 'python' if using pip instead of uv.
        """,
        "diagnose": """
🔍 DIAGNOSE COMMAND:
  Run system diagnostics and health checks.
  
  Usage: uv run main.py diagnose [options]
  
  Options:
    --full           Run full diagnostic suite
    --chrome         Check Chrome installation
    --deps           Check Python dependencies
    --config         Check configuration
    --network        Test network connectivity
    --export         Export report to file
  
  Examples:
    uv run main.py diagnose --full
    uv run main.py diagnose --chrome --export report.json
    
  Note: Replace 'uv run' with 'python' if using pip instead of uv.
        """
    }
    
    if topic in help_topics:
        print(help_topics[topic])
    else:
        print(f"❌ No help available for topic: {topic}")
        print("Available topics: run, launch, diagnose")

def show_general_help():
    """Show general help information with colors."""
    print(f"""
{Colors.BRIGHT_CYAN}🔍 BROWSER AGENT HELP:{Colors.RESET}

The Browser Agent is an AI-powered tool that controls web browsers through natural language commands.

{Colors.BRIGHT_YELLOW}MAIN COMMANDS:{Colors.RESET}
  {Colors.BRIGHT_GREEN}run{Colors.RESET}         Start the browser agent (default)
  {Colors.BRIGHT_GREEN}launch{Colors.RESET}      Launch Chrome with debugging
  {Colors.BRIGHT_GREEN}connect{Colors.RESET}     Connect to existing Chrome instance
  {Colors.BRIGHT_GREEN}profiles{Colors.RESET}    Manage browser profiles
  {Colors.BRIGHT_GREEN}diagnose{Colors.RESET}    Run system diagnostics
  {Colors.BRIGHT_GREEN}clean{Colors.RESET}       Clean up temporary files
  {Colors.BRIGHT_GREEN}config{Colors.RESET}      Manage configuration
  {Colors.BRIGHT_GREEN}version{Colors.RESET}     Show version information
  {Colors.BRIGHT_GREEN}help{Colors.RESET}        Show this help

{Colors.BRIGHT_YELLOW}GETTING STARTED:{Colors.RESET}
  1. Set up your OpenAI API key in a .env file
  2. Launch Chrome: {Colors.BRIGHT_CYAN}uv run main.py launch{Colors.RESET} (or {Colors.BRIGHT_CYAN}python main.py launch{Colors.RESET})
  3. Run the agent: {Colors.BRIGHT_CYAN}uv run main.py run{Colors.RESET} (or {Colors.BRIGHT_CYAN}python main.py run{Colors.RESET})

{Colors.BRIGHT_YELLOW}PROFILE TYPES:{Colors.RESET}
  {Colors.BRIGHT_MAGENTA}temp{Colors.RESET}        Temporary profile (clean session)
  {Colors.BRIGHT_MAGENTA}default{Colors.RESET}     Default browser profile (saved logins, bookmarks, history)

For detailed help on a specific command:
  {Colors.BRIGHT_CYAN}uv run main.py help <command>{Colors.RESET} (or {Colors.BRIGHT_CYAN}python main.py help <command>{Colors.RESET})

For more information, visit: {Colors.BRIGHT_BLUE}{Colors.UNDERLINE}https://github.com/your-repo/browser-agent{Colors.RESET}
    """)
def main():
    """Main CLI entry point with comprehensive command handling."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Handle quiet mode
    if hasattr(args, 'quiet') and args.quiet:
        sys.stdout = open(os.devnull, 'w')
    
    # Handle no-color option
    if hasattr(args, 'no_color') and args.no_color:
        os.environ['NO_COLOR'] = '1'
    
    # Show banner unless suppressed
    if not hasattr(args, 'no_banner') or not args.no_banner:
        if not hasattr(args, 'quiet') or not args.quiet:
            print_banner()
    
    # Set verbose mode globally
    if hasattr(args, 'verbose') and args.verbose:
        args.verbose = True
    else:
        args.verbose = False
    
    # Handle default command
    if not args.command:
        print_status_bar("No command specified, defaulting to 'run'", "INFO")
        from argparse import Namespace
        default_args = Namespace(
            command="run",
            task=None,
            headless=False,
            profile="temp",
            mode=None,
            port=9222,
            timeout=30,
            max_retries=3,
            verbose=args.verbose
        )
        args = default_args
    
    # Command routing with enhanced error handling
    try:
        success = False
        
        if args.command == "run":
            success = command_run(args)
        elif args.command == "launch":
            success = command_launch(args)
        elif args.command == "connect":
            success = command_connect(args)
        elif args.command == "profiles":
            success = command_profiles(args)
        elif args.command == "diagnose":
            success = command_diagnose(args)
        elif args.command == "clean":
            success = command_clean(args)
        elif args.command == "config":
            success = command_config(args)
        elif args.command == "debug":
            success = command_debug(args)
        elif args.command == "version":
            success = command_version(args)
        elif args.command == "help":
            success = command_help(args)
        else:
            print_status_bar(f"Unknown command: {args.command}", "ERROR")
            parser.print_help()
            success = False
        
        # Exit with appropriate code
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_status_bar("\nOperation interrupted by user", "WARNING")
        sys.exit(130)
    except Exception as e:
        print_status_bar(f"Unexpected error: {str(e)}", "ERROR")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def run_cli():
    """Entry point for the CLI."""
    main()

if __name__ == "__main__":
    main()

def setup_terminal():
    """Setup terminal for better interactive experience."""
    # Enable readline history and tab completion if available
    try:
        import readline
        import atexit
        
        # Set up history file
        histfile = os.path.join(os.path.expanduser("~"), ".browser_agent_history")
        try:
            readline.read_history_file(histfile)
            # Default to 1000 lines of history
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass
        
        # Save history on exit
        atexit.register(readline.write_history_file, histfile)
        
        # Enable tab completion
        readline.parse_and_bind('tab: complete')
        
        return True
    except ImportError:
        return False

def reset_cursor():
    """Reset cursor position and clear any hanging output."""
    sys.stdout.write('\r')  # Return to beginning of line
    sys.stdout.flush()

def print_clean_prompt(prompt_text):
    """Print a clean prompt with proper cursor positioning."""
    # Clear the current line and print the prompt
    sys.stdout.write('\r\033[K')  # Clear current line
    sys.stdout.write(prompt_text)
    sys.stdout.flush()

def print_agent_response(response_text: str):
    """Print agent response with proper formatting, cursor handling, and colors."""
    # Ensure we start on a clean line
    sys.stdout.write('\r\033[K')  # Clear current line
    sys.stdout.flush()
    
    separator = "="*50
    print(f"\n{Colors.BRIGHT_MAGENTA}{separator}{Colors.RESET}")
    print(f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}RESPONSE:{Colors.RESET}")
    print(f"{Colors.BRIGHT_MAGENTA}{separator}{Colors.RESET}")
    print(f"{Colors.WHITE}{response_text}{Colors.RESET}")
    print(f"{Colors.BRIGHT_MAGENTA}{separator}{Colors.RESET}")
    
    # Ensure cursor is properly positioned for next prompt
    sys.stdout.flush()