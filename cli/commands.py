"""
Command-line interface for Browser Agent.
"""

import os
import sys
import argparse
import asyncio
from datetime import datetime

from cli.chrome_launcher import launch_chrome_with_debugging
from configurations.config import OPENAI_API_KEY, BROWSER_OPTIONS, BROWSER_CONNECTION

def get_version():
    return "1.0.0"

def print_banner():
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                      🌐 Browser Agent 🌐                     ║
║                        Version {get_version()}                         ║
╚══════════════════════════════════════════════════════════════╝
    An AI agent that controls your browser through natural language
    """
    print(banner)

def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Browser Agent - Control your browser with natural language commands",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # 'run' command (default)
    run_parser = subparsers.add_parser("run", help="Run the browser agent")
    run_parser.add_argument("--task", "-t", type=str, help="Initial task to execute")
    run_parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    # 'launch' command
    launch_parser = subparsers.add_parser("launch", help="Launch Chrome browser with debugging enabled")
    launch_parser.add_argument("--port", "-p", type=int, default=9222, help="Debug port (default: 9222)")
    launch_parser.add_argument("--mode", "-m", choices=["new", "reuse"], 
                             help="Browser launch mode: 'new' or 'reuse' existing")
    
    # 'debug' command
    debug_parser = subparsers.add_parser("debug", help="Run in debug mode with verbose logging")
    debug_parser.add_argument("--task", "-t", type=str, help="Initial task to execute")
    
    # 'version' command
    subparsers.add_parser("version", help="Show version information")
    
    return parser

async def command_run(args):
    from browser.browser_setup import initialize_browser, close_browser
    from browser.controllers.browser_controller import initialize
    from agent.agent import create_agent
    
    if hasattr(args, 'headless') and args.headless:
        BROWSER_OPTIONS["headless"] = True
    
    # Handle Chrome launching
    if BROWSER_CONNECTION.get("use_existing", False):
        port = 9222
        if "cdp_endpoint" in BROWSER_CONNECTION:
            try:
                endpoint = BROWSER_CONNECTION["cdp_endpoint"]
                port = int(endpoint.split(":")[-1])
            except (ValueError, IndexError):
                pass
                
        print("Ensuring Chrome is running with remote debugging...")
        chrome_launched = launch_chrome_with_debugging(port)
        if not chrome_launched and not BROWSER_CONNECTION.get("fallback_to_new", True):
            print("❌ Failed to launch Chrome with debugging and fallback is disabled")
            return
    
    print("Initializing browser...")
    playwright, browser, page = await initialize_browser(BROWSER_OPTIONS, BROWSER_CONNECTION)

    using_connected_browser = BROWSER_CONNECTION.get("use_existing", False)
    
    print("Setting up virtual browser controller...")
    await initialize(page)
    
    print("Creating agent with tools...")
    try:
        agent_executor = await create_agent(OPENAI_API_KEY)
        print("Agent created successfully!")
    except Exception as agent_error:
        print(f"\n❌ ERROR CREATING AGENT: {str(agent_error)}")
        import traceback
        print("\nDetailed traceback:")
        traceback.print_exc()
        return
    
    # Handle initial task if provided
    if hasattr(args, 'task') and args.task:
        print(f"\nExecuting initial task: {args.task}\n")
        start_time = datetime.now()
        
        try:
            response = await agent_executor.ainvoke(args.task)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "="*50)
            print(f"Execution completed in {duration:.2f} seconds")
            print("="*50)
            print(response.get("output", "No output received"))
            print("="*50)
        except Exception as e:
            print(f"\nError executing initial task: {str(e)}")
    
    # Main interaction loop
    keep_running = True
    while keep_running:
        user_query = input("\nEnter your instruction for the browser agent (or type 'exit' to quit): ")
        
        if user_query.lower() in ['exit', 'quit', 'q']:
            break
            
        print(f"\nExecuting: {user_query}\n")
        start_time = datetime.now()
        
        try:
            response = await agent_executor.ainvoke(user_query)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "="*50)
            print(f"Execution completed in {duration:.2f} seconds")
            print("="*50)
            print(response.get("output", "No output received"))
            print("="*50)
                
        except Exception as e:
            print(f"\nError during execution: {str(e)}")
            print("The agent encountered an error but the browser will remain open.")
            print("You can continue with a new instruction or type 'exit' to quit.")
    
    # Clean up
    if 'playwright' in locals() and 'browser' in locals():
        if using_connected_browser:
            close_input = input("\nDisconnect from browser? (y/n): ")
        else:
            close_input = input("\nClose browser? (y/n): ")
            
        if close_input.lower() == 'y':
            print("Cleaning up browser resources...")
            await close_browser(playwright, browser, is_connected=using_connected_browser)
        else:
            print("Browser left open. You can close it manually.")

async def command_launch(args):
    port = args.port
    mode = None
    
    if args.mode:
        if args.mode == "new":
            mode = "new_window"
        elif args.mode == "reuse":
            mode = "close_reopen"
    
    print(f"Launching Chrome with debugging on port {port}...")
    success = launch_chrome_with_debugging(port=port, mode=mode)
    
    if success:
        print(f"✅ Chrome is now running with remote debugging on port {port}")
        print(f"To connect to this browser instance, use the CDP endpoint: http://localhost:{port}")
        print("\nYou can now run the Browser Agent with the 'run' command to connect to this instance.")
    else:
        print("❌ Failed to launch Chrome with debugging")

def command_version(args):
    print_banner()
    print("Detailed Information:")
    print(f"  - Version: {get_version()}")
    print(f"  - Python: {sys.version.split()[0]}")
    print(f"  - Platform: {sys.platform}")
    print(f"  - Current directory: {os.getcwd()}")
    print("\nDependencies:")
    try:
        import playwright
        print(f"  - Playwright: {getattr(playwright, '__version__', 'unknown')}")
    except ImportError:
        print("  - Playwright: Not installed")
    
    try:
        import langchain
        print(f"  - LangChain: {getattr(langchain, '__version__', 'unknown')}")
    except ImportError:
        print("  - LangChain: Not installed")

async def command_debug(args):
    print("Running in DEBUG mode with verbose logging")
    
    import logging
    logging.basicConfig(level=logging.DEBUG, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    await command_run(args)

async def main():
    parser = setup_argparse()
    args = parser.parse_args()
    
    print_banner()
    
    if not args.command:
        from argparse import Namespace
        default_args = Namespace(
            command="run",
            task=None,
            headless=False
        )
        args = default_args
        print("No command specified, defaulting to 'run'")
    
    if args.command == "run":
        await command_run(args)
    elif args.command == "launch":
        await command_launch(args)
    elif args.command == "debug":
        await command_debug(args)
    elif args.command == "version":
        command_version(args)
    else:
        parser.print_help()

def run_cli():
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())