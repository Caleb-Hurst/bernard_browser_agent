import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM Provider Configuration
# Choose your preferred provider: "openai", "azure", "groq", "anthropic"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Default to Groq

# LLM Provider Settings
LLM_CONFIG = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4o",
        "temperature": 0,
        "max_tokens": 2048,
        "base_url": None,  # Use default OpenAI endpoint
    },
    "azure": {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "model": "gpt-4o",
        "temperature": 0,
        "max_tokens": 2048,
        "azure_endpoint": os.getenv("AZURE_ENDPOINT"),
        "api_version": "2024-12-01-preview",
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
        "model": "openai/gpt-oss-120b",
        "temperature": 0,
        "max_tokens": 2048,
    },
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0,
        "max_tokens": 2048,
    }
}

# Get the current provider configuration
CURRENT_LLM_CONFIG = LLM_CONFIG.get(LLM_PROVIDER, LLM_CONFIG["groq"])

# Validate that the selected provider has an API key
if not CURRENT_LLM_CONFIG.get("api_key"):
    available_providers = [provider for provider, config in LLM_CONFIG.items() if config.get("api_key")]
    if available_providers:
        print(f"Warning: No API key found for {LLM_PROVIDER}. Available providers with API keys: {', '.join(available_providers)}")
        # Fallback to first available provider
        LLM_PROVIDER = available_providers[0]
        CURRENT_LLM_CONFIG = LLM_CONFIG[LLM_PROVIDER]
        print(f"Switching to {LLM_PROVIDER} provider.")
    else:
        raise ValueError("No LLM provider API keys found. Please set at least one API key in your environment variables.")

# Set environment variables for libraries that need them directly
if CURRENT_LLM_CONFIG.get("api_key"):
    os.environ[f"{LLM_PROVIDER.upper()}_API_KEY"] = CURRENT_LLM_CONFIG["api_key"]

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

# Performance optimization settings
PERFORMANCE_MODE = {
    "fast_mode": os.getenv("FAST_MODE", "true").lower() == "true",  # Enable fast mode by default
    "minimal_delays": True,  # Use minimal delays for maximum speed
    "optimize_mouse_movement": True,  # Use optimized mouse paths
    "reduce_transitions": True,  # Reduce CSS transition times
}

# Browser connection options
BROWSER_CONNECTION = {
    "use_existing": True,  # Connect to existing browser
    "cdp_endpoint": "http://localhost:9222",
    "fallback_to_new": True  # If connection fails, launch a new browser
}