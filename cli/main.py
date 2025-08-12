"""
Main CLI entry point - streamlined and modular.
"""

import os
import sys
from argparse import Namespace

from cli.core import print_banner, print_status_bar
from cli.parsers import setup_argparse
from cli.handlers import (
    command_run, command_launch, command_connect, command_profiles,
    command_diagnose, command_clean, command_config, command_version,
    command_help, command_debug
)

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
            success = False
        
        # Exit with appropriate code
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_status_bar("\nOperation interrupted by user", "WARNING")
        sys.exit(130)
    except Exception as e:
        print_status_bar(f"Unexpected error: {str(e)}", "ERROR")
        if getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()
        sys.exit(1)

def run_cli():
    """Entry point for the CLI."""
    main()

if __name__ == "__main__":
    main()
