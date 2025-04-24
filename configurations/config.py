import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API Keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set environment variables for libraries that need them directly
if OPENAI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = OPENAI_API_KEY

# Browser launch options
BROWSER_OPTIONS = {
    "headless": os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
    "channel": "chrome",
    "args": [
        "--start-maximized",
        "--disable-notifications",
        "--disable-extensions"
    ]
}

# Browser connection options
BROWSER_CONNECTION = {
    "use_existing": True,  # Connect to existing browser
    "cdp_endpoint": "http://localhost:9222",
    "fallback_to_new": True  # If connection fails, launch a new browser
}