import os
import platform
import subprocess
import time
import socket
import sys
import psutil
import shutil
import tempfile
import json
from pathlib import Path

def is_port_in_use(port, host="127.0.0.1"):
    """Check if the specified port is already in use on the given host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result == 0
    except:
        return False

def create_debug_profile_with_copies(source_dir, dest_dir):
    """Create a debug profile by copying essential data from actual Chrome profile."""
    try:
        source_path = Path(source_dir)
        dest_path = Path(dest_dir)
        
        # Remove existing debug profile
        if dest_path.exists():
            shutil.rmtree(dest_path)
        
        # Create destination directory
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Copy Local State (needed for Chrome to start)
        local_state_source = source_path / "Local State"
        local_state_dest = dest_path / "Local State"
        if local_state_source.exists():
            shutil.copy2(local_state_source, local_state_dest)
            print("✓ Copied Local State")
        
        # Create Default profile directory
        default_profile_dest = dest_path / "Default"
        default_profile_dest.mkdir(parents=True, exist_ok=True)
        
        # Items to copy (safer than symlinks for debugging)
        copy_items = [
            'Bookmarks',
            'Login Data',
            'Web Data', 
            'Cookies'
            # Exclude 'Preferences' as it contains sync settings that trigger signin
        ]
        
        source_default = source_path / "Default"
        copied_items = []
        
        # Copy essential profile data
        for item in copy_items:
            source_item = source_default / item
            dest_item = default_profile_dest / item
            
            if source_item.exists():
                try:
                    if source_item.is_file():
                        shutil.copy2(source_item, dest_item)
                        copied_items.append(item)
                    elif source_item.is_dir():
                        shutil.copytree(source_item, dest_item, dirs_exist_ok=True)
                        copied_items.append(item)
                except Exception as e:
                    print(f"⚠️ Could not copy {item}: {e}")
        
        # Create a minimal First Run file to avoid setup dialogs
        first_run_file = dest_path / "First Run"
        if not first_run_file.exists():
            first_run_file.touch()
        
        # Create a clean preferences file without sync settings
        preferences_file = default_profile_dest / "Preferences"
        if not preferences_file.exists():
            clean_preferences = {
                "profile": {
                    "name": "Debug Profile",
                    "managed_user_id": "",
                    "content_settings": {},
                    "default_content_setting_values": {}
                },
                "browser": {
                    "show_home_button": False,
                    "check_default_browser": False
                },
                "signin": {
                    "allowed": False
                },
                "sync": {
                    "suppress_sync_promo": True
                }
            }
            with open(preferences_file, 'w') as f:
                json.dump(clean_preferences, f, indent=2)
            
        if copied_items:
            print(f"✓ Copied {len(copied_items)} profile items: {', '.join(copied_items)}")
            return True
        else:
            print("⚠️ No profile data found to copy, creating minimal profile")
            return True  # Still return True to continue with empty profile
            
    except Exception as e:
        print(f"❌ Error creating debug profile: {e}")
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
        use_default_profile: Whether to use default profile (True) or temporary profile (False)
        mode: How to handle existing Chrome sessions
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if debugging port is already in use
    if is_port_in_use(port, "127.0.0.1"):
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
            
            # Ask about profile preference after choosing the mode
            print("\nProfile options:")
            print("1. Use default profile (saved logins, bookmarks, history)")
            print("2. Use temporary profile (clean session)")
            profile_choice = input("Enter 1 or 2: ").strip()
            
            if profile_choice == "1":
                use_default_profile = True
            else:
                use_default_profile = False
        
        if mode == "close_reopen":
            print("Closing Chrome and reopening with debugging enabled...")
            close_chrome()
            time.sleep(3)  # Wait longer for Chrome to fully close
            chrome_running = False
        elif mode == "new_window":
            print("Opening new Chrome window with debugging...")
            # For new window mode with default profile, warn about Chrome limitation
            if use_default_profile:
                print("⚠️ Note: New window mode with default profile may have limitations")
                print("    Chrome might not fully separate the debug session from existing windows")
            chrome_running = False  # Proceed with launch
    else:
        # Chrome is not running, ask about profile preference
        print("Profile options:")
        print("1. Use default profile (saved logins, bookmarks, history)")
        print("2. Use temporary profile (clean session)")
        profile_choice = input("Enter 1 or 2: ").strip()
        
        if profile_choice == "1":
            use_default_profile = True
        else:
            use_default_profile = False
    
    # Launch Chrome with debugging
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            # Use direct Chrome executable path
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            
            if use_default_profile:
                print("🔐 Using default browser profile (saved logins, bookmarks, history)...")
                
                # Create a dedicated debug profile with user data
                default_profile_dir = Path(os.path.expanduser("~/Library/Application Support/Google/Chrome"))
                debug_profile_dir = Path(os.path.expanduser("~/Library/Application Support/Google/ChromeDebugProfile"))
                
                # Create/update the debug profile with copies of your actual data
                print("📁 Setting up debug profile with access to your data...")
                link_success = create_debug_profile_with_copies(default_profile_dir, debug_profile_dir)
                
                if not link_success:
                    print("⚠️ Could not set up debug profile, using minimal profile")
                    debug_profile_dir.mkdir(parents=True, exist_ok=True)
                
                cmd = [
                    chrome_path,
                    f"--remote-debugging-port={port}",
                    f"--remote-debugging-address=127.0.0.1",
                    "--remote-allow-origins=*",
                    "--no-first-run",
                    "--no-default-browser-check", 
                    "--disable-features=VizDisplayCompositor",
                    "--disable-background-mode",
                    "--disable-sync",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--disable-default-apps",
                    "--disable-extensions-http-throttling",
                    "--disable-signin-promo",
                    "--disable-signin-scoped-device-id",
                    "--disable-background-networking",
                    "--disable-client-side-phishing-detection",
                    "--disable-component-update",
                    "--disable-domain-reliability",
                    f"--user-data-dir={debug_profile_dir}"
                ]
                
                print("✓ Using debug profile with your Chrome data")
            else:
                print("🔐 Using temporary profile for clean browser sessions...")
                
                # Create a unique temporary profile directory
                temp_profile_dir = Path(tempfile.mkdtemp(prefix="chrome_debug_temp_"))
                
                cmd = [
                    chrome_path,
                    f"--remote-debugging-port={port}",
                    f"--remote-debugging-address=127.0.0.1",
                    "--remote-allow-origins=*",
                    "--disable-features=VizDisplayCompositor",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-mode",
                    "--disable-sync",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--disable-default-apps",
                    "--disable-extensions-http-throttling",
                    "--disable-signin-promo",
                    "--disable-signin-scoped-device-id",
                    "--disable-background-networking",
                    "--disable-client-side-phishing-detection",
                    "--disable-component-update",
                    "--disable-domain-reliability",
                    f"--user-data-dir={temp_profile_dir}"
                ]
                
                print(f"✓ Using temporary profile: {temp_profile_dir}")
            
            print(f"Executing: {' '.join(cmd)}")
            # Launch Chrome with proper process handling
            chrome_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🚀 Launched Chrome on macOS with debugging port {port}")
            
        else:
            print(f"❌ Unsupported operating system: {system}")
            return False
            
        # Wait for Chrome to start and open the debugging port
        print("Giving Chrome time to start...")
        time.sleep(4)  # Give Chrome more time to initialize with real profile
        
        max_attempts = 20  # Increase attempts for real profile
        for attempt in range(max_attempts):
            # Check if the port is open
            if is_port_in_use(port, "127.0.0.1"):
                print(f"✅ Verified Chrome is running with debugging port {port}")
                # Additional verification - try to connect to the debugging endpoint
                try:
                    import urllib.request
                    import json
                    url = f"http://127.0.0.1:{port}/json/version"
                    with urllib.request.urlopen(url, timeout=3) as response:
                        data = json.loads(response.read().decode())
                        print(f"✅ Chrome debugging API is responding (Browser: {data.get('Browser', 'Unknown')})")
                        return True
                except Exception as e:
                    print(f"⚠️ Port {port} is open but API not ready yet (attempt {attempt+1})...")
                    time.sleep(1)
                    continue
                
                return True
                
            print(f"Waiting for Chrome to start (attempt {attempt+1}/{max_attempts})...")
            time.sleep(1)
            
        print("⚠️ Chrome started but debugging port is not responding")
        print("This might be due to Chrome's security restrictions")
        print("Try restarting Chrome or using a different port")
        return False
        
    except Exception as e:
        print(f"❌ Error launching Chrome: {str(e)}")
        return False

def close_chrome():
    """Close Chrome browser."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            # Try graceful quit first
            subprocess.run(["osascript", "-e", 'quit app "Google Chrome"'], check=False)
            time.sleep(2)  # Wait longer for graceful shutdown
            
            # Then force kill any remaining processes
            subprocess.run(["pkill", "-f", "Google Chrome"], check=False)
            time.sleep(1)
            subprocess.run(["killall", "-9", "Google Chrome"], check=False)
            
            print("✅ Chrome closed successfully")
        return True
    except Exception as e:
        print(f"❌ Error closing Chrome: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the launcher when run directly
    launch_chrome_with_debugging()
