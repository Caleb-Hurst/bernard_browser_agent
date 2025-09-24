#!/usr/bin/env python3
"""
GitHub Actions integration for Browser Agent
Allows the browser agent to be called programmatically from GitHub workflows
"""

import os
import sys
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.agent import create_agent
from browser.browser_setup import initialize_browser, close_browser
from browser.controllers.browser_controller import initialize
from configurations.config import BROWSER_OPTIONS, BROWSER_CONNECTION
from cli.chrome_launcher import launch_chrome_with_debugging

class GitHubBrowserAgent:
    """Browser Agent wrapper for GitHub Actions integration"""
    
    def __init__(self, headless: bool = True, timeout: int = 300):
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.page = None
        self.agent = None
        
    def setup(self) -> bool:
        """Initialize the browser agent"""
        print("🔧 Setting up Browser Agent for GitHub Actions...")
        
        try:
            # Configure for headless operation in CI
            BROWSER_OPTIONS["headless"] = self.headless
            BROWSER_OPTIONS["timeout"] = self.timeout * 1000  # Convert to milliseconds
            
            # Launch Chrome with debugging if needed
            if not self.headless:
                print("🌐 Launching Chrome with debugging...")
                chrome_launched = launch_chrome_with_debugging(port=9222, use_default_profile=False)
                if not chrome_launched:
                    print("❌ Failed to launch Chrome")
                    return False
            
            # Initialize browser
            print("🌐 Initializing browser...")
            self.playwright, self.browser, self.page = initialize_browser(BROWSER_OPTIONS, BROWSER_CONNECTION)
            
            # Initialize browser controller
            print("🎮 Setting up browser controller...")
            initialize(self.page)
            
            # Create agent
            print("🤖 Creating AI agent...")
            self.agent = create_agent()
            
            print("✅ Browser Agent setup complete!")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {str(e)}")
            return False
    
    def execute_test_scenario(self, scenario: str) -> Dict[str, Any]:
        """Execute a test scenario and return results"""
        if not self.agent:
            return {"success": False, "error": "Agent not initialized"}
        
        print(f"🧪 Executing test scenario: {scenario}")
        
        try:
            # Execute the scenario
            response = self.agent.invoke(scenario)
            
            result = {
                "success": True,
                "scenario": scenario,
                "output": response.get("output", ""),
                "input": response.get("input", scenario),
                "messages": len(response.get("messages", []))
            }
            
            print("✅ Test scenario completed successfully!")
            return result
            
        except Exception as e:
            print(f"❌ Test scenario failed: {str(e)}")
            return {
                "success": False,
                "scenario": scenario,
                "error": str(e)
            }
    
    def cleanup(self):
        """Clean up browser resources"""
        print("🧹 Cleaning up browser resources...")
        if self.playwright and self.browser:
            try:
                close_browser(self.playwright, self.browser, is_connected=False)
                print("✅ Cleanup complete!")
            except Exception as e:
                print(f"⚠️ Cleanup warning: {str(e)}")

def main():
    """Main entry point for GitHub Actions"""
    if len(sys.argv) < 2:
        print("Usage: python github_integration.py '<test_scenario>'")
        sys.exit(1)
    
    # Get test scenario from command line
    test_scenario = sys.argv[1]
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    timeout = int(os.getenv("TIMEOUT", "300"))
    
    # Initialize agent
    agent = GitHubBrowserAgent(headless=headless, timeout=timeout)
    
    try:
        # Setup
        if not agent.setup():
            print("❌ Failed to setup browser agent")
            sys.exit(1)
        
        # Execute test
        result = agent.execute_test_scenario(test_scenario)
        
        # Output results for GitHub Actions
        print("\n" + "="*60)
        print("TEST RESULTS:")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        # Set GitHub Actions outputs
        if os.getenv("GITHUB_ACTIONS"):
            output_text = result.get('output', '').replace('%', '%25').replace('\n', '%0A').replace('\r', '%0D')
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"test_success={str(result['success']).lower()}\n")
                f.write(f"test_output={output_text}\n")
        
        # Exit with appropriate code
        sys.exit(0 if result["success"] else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        agent.cleanup()

if __name__ == "__main__":
    main()