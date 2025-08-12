"""
Debug command implementation.
"""

import logging
from argparse import Namespace
from cli.core import print_status_bar

def command_debug(args):
    """Run in debug mode with verbose logging."""
    print_status_bar("Starting DEBUG mode with verbose logging", "INFO")
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
    from .run import command_run
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
