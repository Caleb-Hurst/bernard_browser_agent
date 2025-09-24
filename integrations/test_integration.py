#!/usr/bin/env python3
"""
Local testing script for GitHub integration
Test the browser agent integration before deploying to GitHub Actions
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from integrations.github_integration import GitHubBrowserAgent

def test_browser_agent():
    """Test the browser agent with a simple scenario"""
    print("🧪 Testing Browser Agent Integration")
    print("=" * 50)
    
    # Test scenario
    test_scenario = """
    Go to https://httpbin.org/forms/post and fill out the form with test data:
    - Customer name: John Doe  
    - Telephone: 555-1234
    - Email: john.doe@example.com
    - Small comment: This is a test submission
    Then submit the form and verify the response shows the submitted data.
    """
    
    # Initialize agent (headless for testing)
    agent = GitHubBrowserAgent(headless=True, timeout=120)
    
    try:
        # Setup
        print("🔧 Setting up browser agent...")
        if not agent.setup():
            print("❌ Failed to setup browser agent")
            return False
        
        # Execute test
        print("🚀 Executing test scenario...")
        result = agent.execute_test_scenario(test_scenario)
        
        # Display results
        print("\n" + "="*60)
        print("TEST RESULTS:")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        return result["success"]
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        agent.cleanup()

def test_scenario_generation():
    """Test the test scenario generation"""
    print("\n🧪 Testing Scenario Generation")
    print("=" * 50)
    
    # Mock issue data
    issue_title = "Login form validation is not working"
    issue_body = """
    When users enter invalid email addresses in the login form, the validation message doesn't appear.
    
    Steps to reproduce:
    1. Go to /login
    2. Enter invalid email like 'notanemail'
    3. Click submit
    
    Expected: Validation error should appear
    Actual: Form submits without validation
    """
    
    # This would normally call the OpenAI API
    print(f"Issue Title: {issue_title}")
    print(f"Issue Body: {issue_body}")
    print("\n📝 Generated Test Scenario:")
    print("Navigate to the login page, test email validation by entering invalid formats, and verify error messages appear correctly.")

def main():
    """Main test runner"""
    print("🚀 Browser Agent GitHub Integration Test Suite")
    print("=" * 60)
    
    # Check environment
    required_env_vars = ["GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("At least one API key is required for the LLM provider")
    
    # Test scenario generation
    test_scenario_generation()
    
    # Test browser agent
    success = test_browser_agent()
    
    if success:
        print("\n✅ All tests passed! Integration is ready for GitHub Actions.")
    else:
        print("\n❌ Tests failed. Please check the setup and try again.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())