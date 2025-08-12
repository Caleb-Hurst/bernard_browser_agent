"""
Legacy CLI entry point - now redirects to modular CLI.
This file is kept for backward compatibility.
"""

def run_cli():
    """Legacy function - redirects to new modular CLI."""
    from .main import run_cli as new_run_cli
    return new_run_cli()

def main():
    """Legacy function - redirects to new modular CLI."""
    from .main import main as new_main
    return new_main()

# Re-export for compatibility
__all__ = ['main', 'run_cli']

if __name__ == "__main__":
    main()
