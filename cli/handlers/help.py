"""
Help command implementation.
"""

from cli.core import Colors

def command_help(args):
    """Show detailed help for commands."""
    if args.topic:
        show_command_help(args.topic)
    else:
        show_general_help()
    return True

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
  1. Set up your API key in a .env file
  2. Launch Chrome: {Colors.BRIGHT_CYAN}uv run main.py launch{Colors.RESET} (or {Colors.BRIGHT_CYAN}python main.py launch{Colors.RESET})
  3. Run the agent: {Colors.BRIGHT_CYAN}uv run main.py run{Colors.RESET} (or {Colors.BRIGHT_CYAN}python main.py run{Colors.RESET})

{Colors.BRIGHT_YELLOW}PROFILE TYPES:{Colors.RESET}
  {Colors.BRIGHT_MAGENTA}temp{Colors.RESET}        Temporary profile (clean session)
  {Colors.BRIGHT_MAGENTA}default{Colors.RESET}     Default browser profile (saved logins, bookmarks, history)

For detailed help on a specific command:
  {Colors.BRIGHT_CYAN}uv run main.py help <command>{Colors.RESET} (or {Colors.BRIGHT_CYAN}python main.py help <command>{Colors.RESET})

For more information, visit: {Colors.BRIGHT_BLUE}{Colors.UNDERLINE}https://github.com/your-repo/browser-agent{Colors.RESET}
    """)
