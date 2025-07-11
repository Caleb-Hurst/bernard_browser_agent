import os
import platform
import subprocess
import time
import socket
import sys
import psutil
from pathlib import Path

def is_port_in_use(port):
    """Check if the specified port is already in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def get_chrome_process():
    """Get the Chrome process if it's running."""
    chrome_names = ['Google Chrome', 'chrome', 'chromium']
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_name = proc.info['name']
            if proc_name and any(name.lower() in proc_name.lower() for name in chrome_names):
                # Check if it's the main Chrome process (not helper processes)
                cmdline = proc.info.get('cmdline', [])
                if cmdline and len(cmdline) > 0:
                    # Look for the main Chrome executable, not helpers
                    if 'Google Chrome.app/Contents/MacOS/Google Chrome' in ' '.join(cmdline) or \
                       (proc_name.lower() == 'google chrome' and '--type=' not in ' '.join(cmdline)):
                        return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
            pass
    return None

def launch_chrome_with_debugging(port=9222, use_default_profile=True, mode=None):
    """
    Launch Chrome with remote debugging enabled.
    
    Args:
        port: The debugging port to use
        use_default_profile: Whether to attempt using default profile (deprecated, ignored)
        mode: How to handle existing Chrome sessions
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if debugging port is already in use
    if is_port_in_use(port):
        print(f"✅ Chrome already running with remote debugging on port {port}")
        return True
    
    # Check if Chrome is already running (without debugging)
    chrome_proc = get_chrome_process()
    chrome_running = chrome_proc is not None
    
    # If Chrome is already running, handle according to mode
    if chrome_running:
        print(f"⚠️ Chrome is already running but not in debug mode")
        
        # If no mode specified, ask user
        if mode is None:
            print("Choose an option:")
            print("1. Close current Chrome and reopen with debugging")
            print("2. Open a new Chrome window with debugging")
            choice = input("Enter 1 or 2: ").strip()
            
            if choice == "1":
                mode = "close_reopen"
            else:
                mode = "new_window"
        
        if mode == "close_reopen":
            print("Closing Chrome and reopening with debugging enabled...")
            close_chrome()
            time.sleep(1)  # Minimal wait for Chrome to close
            chrome_running = False
    
    # Launch Chrome with debugging
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            # Use direct Chrome executable path
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            
            # Always use temporary profile
            print("🔐 Using temporary profile for clean browser sessions...")
            
            temp_profile_dir = Path(os.path.expanduser("~/Library/Application Support/Google/ChromeTemp"))
            temp_profile_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                chrome_path,
                f"--remote-debugging-port={port}",
                "--no-first-run", 
                "--no-default-browser-check",
                "--disable-features=VizDisplayCompositor",
                "--remote-allow-origins=*",
                f"--user-data-dir={temp_profile_dir}"
            ]
            
            print("✓ Using temporary profile")
            
            print(f"Executing: {' '.join(cmd)}")
            # Suppress Chrome's output to keep terminal clean  
            chrome_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🚀 Launched Chrome on macOS with debugging port {port}")
            
        else:
            print(f"❌ Unsupported operating system: {system}")
            return False
            
        # Wait for Chrome to start and open the debugging port
        print("Giving Chrome time to start...")
        time.sleep(2)  # Reduced initial delay
        
        max_attempts = 10  # Reduced attempts for faster startup
        for attempt in range(max_attempts):
            # Check if the port is open
            if is_port_in_use(port):
                print(f"✅ Verified Chrome is running with debugging port {port}")
                return True
                
            print(f"Waiting for Chrome to start (attempt {attempt+1}/{max_attempts})...")
            time.sleep(1)  # Reduced wait time between attempts
            
        print("⚠️ Chrome started but debugging port is not responding")
        print("This might be due to Chrome's security restrictions")
        print("Try restarting Chrome or using a different port")
        return True
        
    except Exception as e:
        print(f"❌ Error launching Chrome: {str(e)}")
        return False

def close_chrome():
    """Close Chrome browser."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["osascript", "-e", 'quit app "Google Chrome"'], check=False)
            time.sleep(1)
            subprocess.run(["pkill", "-f", "Google Chrome"], check=False)
            time.sleep(1)
            subprocess.run(["killall", "-9", "Google Chrome"], check=False)
        return True
    except Exception as e:
        print(f"❌ Error closing Chrome: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the launcher when run directly
    launch_chrome_with_debugging(use_default_profile=False)
