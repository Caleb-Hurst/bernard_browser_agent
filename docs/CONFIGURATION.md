# ⚙️ Configuration Guide

Complete guide to configuring the Browser Agent for your needs.

## Configuration Files

The Browser Agent uses several configuration methods:

1. **Environment Variables** (highest priority)
2. **`.env` file** (medium priority)
3. **`configurations/config.py`** (default values)

## LLM Provider Configuration

### Choosing a Provider

Set your preferred LLM provider using the `LLM_PROVIDER` environment variable:

```bash
export LLM_PROVIDER=groq  # Options: openai, azure, groq, anthropic
```

### Provider-Specific Settings

Each provider has its own configuration requirements:

#### OpenAI

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_api_key_here
```

#### Azure OpenAI

```bash
export LLM_PROVIDER=azure
export AZURE_OPENAI_API_KEY=your_api_key_here
export AZURE_ENDPOINT=https://your-resource-name.openai.azure.com/
```

#### Groq

```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=your_api_key_here
```

#### Anthropic

```bash
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your_api_key_here
```

## Browser Configuration

### Basic Browser Options

Configure browser behavior in your `.env` file:

```bash
# Browser window visibility
BROWSER_HEADLESS=false

# Performance optimization
FAST_MODE=true

# Default timeout for operations (seconds)
DEFAULT_TIMEOUT=30
```

### Advanced Browser Configuration

Edit `configurations/config.py` for advanced browser settings:

```python
BROWSER_OPTIONS = {
    "headless": os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
    "channel": "chrome",  # Browser channel to use
    "args": [
        "--start-maximized",
        "--disable-notifications",
        "--disable-extensions",
        "--disable-web-security",  # For local development only
    ],
    "viewport": {
        "width": 1920,
        "height": 1080
    },
    "timeout": 30000,  # milliseconds
}
```

### Browser Connection Settings

Configure how the agent connects to browsers:

```python
BROWSER_CONNECTION = {
    "use_existing": True,  # Try to connect to existing browser first
    "cdp_endpoint": "http://localhost:9222",  # Chrome DevTools Protocol endpoint
    "fallback_to_new": True,  # Launch new browser if connection fails
    "retry_attempts": 3,
    "retry_delay": 1000,  # milliseconds
}
```

## Performance Configuration

### Performance Mode Settings

Optimize the agent for speed or reliability:

```python
PERFORMANCE_MODE = {
    "fast_mode": os.getenv("FAST_MODE", "true").lower() == "true",
    "minimal_delays": True,  # Reduce artificial delays
    "optimize_mouse_movement": True,  # Use direct cursor movements
    "reduce_transitions": True,  # Minimize CSS transition times
    "aggressive_timeouts": False,  # Use shorter timeouts for faster failure
}
```

### Timeout Configuration

Set various timeout values:

```bash
# General operation timeout
DEFAULT_TIMEOUT=30

# Page load timeout
PAGE_LOAD_TIMEOUT=30

# Element wait timeout
ELEMENT_WAIT_TIMEOUT=10

# Network request timeout
NETWORK_TIMEOUT=30
```

## Model Configuration

### Customizing LLM Models

You can customize which models to use for each provider in `configurations/config.py`:

```python
LLM_CONFIG = {
    "openai": {
        "model": "gpt-4o",  # or "gpt-3.5-turbo", "gpt-4-turbo"
        "temperature": 0,
        "max_tokens": 2048,
    },
    "groq": {
        "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
        # Alternative models:
        # "mixtral-8x7b-32768"
        # "llama2-70b-4096"
        "temperature": 0,
        "max_tokens": 2048,
    },
    # ... other providers
}
```

### Model Parameters

Adjust model behavior:

- **temperature**: Controls creativity (0 = deterministic, 1 = creative)
- **max_tokens**: Maximum response length
- **top_p**: Nucleus sampling parameter
- **frequency_penalty**: Reduces repetition

## Logging Configuration

### Log Levels

Set the logging level:

```bash
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Log Output

Configure where logs are written:

```python
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": {
        "console": True,
        "file": {
            "enabled": False,
            "filename": "browser_agent.log",
            "max_size": "10MB",
            "backup_count": 5,
        }
    }
}
```

## Security Configuration

### Safe Browsing

Configure security settings:

```python
SECURITY_CONFIG = {
    "allow_downloads": False,  # Block file downloads
    "block_popups": True,      # Block popup windows
    "disable_plugins": True,   # Disable browser plugins
    "sandbox": True,           # Run in sandboxed mode
    "private_mode": False,     # Use private/incognito mode
}
```

### Content Filtering

Filter out sensitive content:

```python
CONTENT_FILTER = {
    "block_ads": True,         # Block advertisements
    "block_trackers": True,    # Block tracking scripts
    "block_malware": True,     # Block known malware sites
    "allowed_domains": [],     # Whitelist specific domains
    "blocked_domains": [],     # Blacklist specific domains
}
```

## Profile Configuration

### Default Profile Settings

Configure default browser profile behavior:

```python
PROFILE_CONFIG = {
    "default_profile": "default",
    "auto_create_temp": True,     # Create temporary profiles automatically
    "cleanup_on_exit": True,      # Clean up temporary profiles
    "preserve_sessions": False,   # Save session data
    "enable_extensions": False,   # Allow browser extensions
}
```

### Profile Storage

Configure where profiles are stored:

```bash
export PROFILE_DIR=/path/to/profiles
export TEMP_PROFILE_DIR=/tmp/browser_agent_profiles
```

## Development Configuration

### Debug Settings

For development and debugging:

```python
DEBUG_CONFIG = {
    "slow_mode": False,           # Add delays for observation
    "screenshot_on_error": True,  # Take screenshots on failures
    "save_page_source": False,    # Save HTML on errors
    "verbose_element_info": True, # Detailed element information
    "trace_mode": False,          # Enable execution tracing
}
```

### Testing Configuration

For automated testing:

```python
TEST_CONFIG = {
    "headless": True,
    "disable_images": True,
    "disable_javascript": False,
    "disable_css": False,
    "mock_user_agent": "BrowserAgent/1.0",
    "viewport": {"width": 1280, "height": 720},
}
```

## Environment File Example

Here's a complete `.env` file example:

```bash
# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here

# Browser Configuration
BROWSER_HEADLESS=false
FAST_MODE=true
DEFAULT_TIMEOUT=30

# Performance
PAGE_LOAD_TIMEOUT=30
ELEMENT_WAIT_TIMEOUT=10

# Logging
LOG_LEVEL=INFO

# Security
ALLOW_DOWNLOADS=false
BLOCK_POPUPS=true

# Development
DEBUG_MODE=false
SLOW_MODE=false
```

## Configuration Validation

The agent automatically validates configuration on startup:

```bash
# Check current configuration
uv run main.py config get

# Validate configuration
uv run main.py diagnose

# Reset to defaults
uv run main.py config reset
```

## Advanced Customization

For advanced users, you can modify the configuration files directly:

- `configurations/config.py` - Main configuration
- `agent/agent.py` - Agent behavior and prompts
- `browser/browser_setup.py` - Browser initialization
- `cli/commands.py` - CLI behavior
