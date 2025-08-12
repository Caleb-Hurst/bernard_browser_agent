"""
Terminal utilities and interactive interface helpers.
"""

import sys
from .colors import Colors, colorize

def setup_terminal():
    """Setup terminal for better interactive experience."""
    # Enable readline history and tab completion if available
    try:
        import readline
        import platform
        import os
        
        # Setup history and tab completion
        readline.parse_and_bind("tab: complete")
        
        # Configure key bindings based on platform
        if platform.system() == "Darwin":  # macOS
            # macOS-specific key bindings for better text editing
            readline.parse_and_bind("set editing-mode emacs")
            
            # Enable meta key (Option) for macOS
            readline.parse_and_bind("set convert-meta off")
            readline.parse_and_bind("set input-meta on")
            readline.parse_and_bind("set output-meta on")
            
            # Ensure history navigation works properly (these are defaults, but explicit is better)
            readline.parse_and_bind("\"\\e[A\": previous-history")     # Up arrow
            readline.parse_and_bind("\"\\e[B\": next-history")         # Down arrow
            readline.parse_and_bind("\"\\C-p\": previous-history")     # Ctrl+P (alternative)
            readline.parse_and_bind("\"\\C-n\": next-history")         # Ctrl+N (alternative)
            
            # Word movement (Option + arrow keys)
            readline.parse_and_bind("\"\\e[1;9C\": forward-word")     # Option+Right
            readline.parse_and_bind("\"\\e[1;9D\": backward-word")    # Option+Left
            readline.parse_and_bind("\"\\e[1;3C\": forward-word")     # Alt+Right (alternative)
            readline.parse_and_bind("\"\\e[1;3D\": backward-word")    # Alt+Left (alternative)
            readline.parse_and_bind("\"\\ef\": forward-word")         # Option+F
            readline.parse_and_bind("\"\\eb\": backward-word")        # Option+B
            
            # Delete word (Option + Delete/Backspace)
            readline.parse_and_bind("\"\\e[3;9~\": kill-word")        # Option+Delete
            readline.parse_and_bind("\"\\ed\": kill-word")            # Option+D
            readline.parse_and_bind("\"\\e[3;3~\": kill-word")        # Alt+Delete (alternative)
            readline.parse_and_bind("\"\\e\\b\": backward-kill-word") # Option+Backspace
            readline.parse_and_bind("\"\\e\\x7f\": backward-kill-word") # Option+Backspace (alternative)
            
            # Line movement (Cmd + arrow keys) - these might not work in all terminals
            readline.parse_and_bind("\"\\e[1;10C\": end-of-line")     # Cmd+Right
            readline.parse_and_bind("\"\\e[1;10D\": beginning-of-line") # Cmd+Left
            readline.parse_and_bind("\"\\e[1;2C\": end-of-line")      # Shift+Right (alternative)
            readline.parse_and_bind("\"\\e[1;2D\": beginning-of-line") # Shift+Left (alternative)
            
            # Delete to end/beginning of line
            readline.parse_and_bind("\"\\e[3;10~\": kill-line")       # Cmd+Delete
            readline.parse_and_bind("\"\\e[1;10K\": backward-kill-line") # Cmd+Backspace
            
            # Standard Emacs shortcuts that work well on macOS
            readline.parse_and_bind("\"\\C-a\": beginning-of-line")   # Ctrl+A
            readline.parse_and_bind("\"\\C-e\": end-of-line")         # Ctrl+E
            readline.parse_and_bind("\"\\C-k\": kill-line")           # Ctrl+K
            readline.parse_and_bind("\"\\C-u\": unix-line-discard")   # Ctrl+U (delete entire line)
            readline.parse_and_bind("\"\\C-w\": backward-kill-word")  # Ctrl+W
            readline.parse_and_bind("\"\\C-y\": yank")                # Ctrl+Y (paste)
            
            # Character movement and deletion
            readline.parse_and_bind("\"\\C-f\": forward-char")        # Ctrl+F
            readline.parse_and_bind("\"\\C-b\": backward-char")       # Ctrl+B
            readline.parse_and_bind("\"\\C-d\": delete-char")         # Ctrl+D
            readline.parse_and_bind("\"\\C-h\": backward-delete-char") # Ctrl+H
            
        else:  # Linux/Windows
            # Standard readline key bindings for other platforms
            readline.parse_and_bind("set editing-mode emacs")
            readline.parse_and_bind("\"\\e[1;5C\": forward-word")     # Ctrl+Right
            readline.parse_and_bind("\"\\e[1;5D\": backward-word")    # Ctrl+Left
            readline.parse_and_bind("\"\\e[3;5~\": kill-word")        # Ctrl+Delete
            readline.parse_and_bind("\"\\C-w\": backward-kill-word")  # Ctrl+W
        
        # Common cross-platform bindings
        readline.parse_and_bind("\"\\C-?\": backward-delete-char")    # Backspace
        readline.parse_and_bind("\"\\e[3~\": delete-char")           # Delete
        readline.parse_and_bind("\"\\e[H\": beginning-of-line")      # Home
        readline.parse_and_bind("\"\\e[F\": end-of-line")            # End
        
        # Enable history
        readline.set_history_length(1000)
        
        # Configure history search
        readline.parse_and_bind("\"\\C-r\": reverse-search-history") # Ctrl+R for reverse search
        readline.parse_and_bind("\"\\C-s\": forward-search-history") # Ctrl+S for forward search
        
        # Try to load history file if it exists
        history_file = os.path.expanduser("~/.browser_agent_history")
        try:
            readline.read_history_file(history_file)
        except FileNotFoundError:
            pass  # No history file yet, that's okay
        except Exception as e:
            # Handle any other history loading issues gracefully
            pass
        
        # Register cleanup function to save history
        import atexit
        atexit.register(lambda: _save_history(history_file))
        
        return True
    except ImportError:
        return False

def _save_history(history_file):
    """Save readline history to file."""
    try:
        import readline
        # Only save if we have actual history
        if readline.get_current_history_length() > 0:
            readline.write_history_file(history_file)
    except (ImportError, IOError, OSError):
        # Fail silently - history saving is not critical
        pass

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
    print(response_text)
    print(f"{Colors.BRIGHT_MAGENTA}{separator}{Colors.RESET}")

def print_banner():
    """Print the application banner."""
    banner = f"""
{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BRIGHT_CYAN}║{Colors.RESET}                      {Colors.BRIGHT_BLUE}🌐 Browser Agent 🌐{Colors.RESET}                     {Colors.BRIGHT_CYAN}║{Colors.RESET}
{Colors.BRIGHT_CYAN}║{Colors.RESET}                        {Colors.BRIGHT_GREEN}Version 1.0.0{Colors.RESET}                         {Colors.BRIGHT_CYAN}║{Colors.RESET}
{Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
    {Colors.CYAN}An AI agent that controls your browser through natural language{Colors.RESET}
    """
    print(banner)
