# 🔍 Troubleshooting Guide

Common issues and solutions for the Browser Agent.

## Installation Issues

### Python Version Problems

**Problem:** Agent fails to start with Python version errors

**Solution:**

```bash
# Check your Python version
python --version

# Must be 3.11 or higher
# If not, install a newer version:
# On macOS with Homebrew:
brew install python@3.11

# On Ubuntu/Debian:
sudo apt update && sudo apt install python3.11
```

### Dependency Installation Failures

**Problem:** `uv sync` or `pip install` fails

**Solutions:**

1. **Update uv or pip:**

   ```bash
   # Update uv
   pip install --upgrade uv

   # Or update pip
   pip install --upgrade pip
   ```

2. **Clear cache:**

   ```bash
   # Clear uv cache
   uv cache clean

   # Clear pip cache
   pip cache purge
   ```

3. **Use verbose output to diagnose:**
   ```bash
   uv sync --verbose
   # or
   pip install -r requirements.txt --verbose
   ```

### Playwright Installation Issues

**Problem:** Playwright browsers fail to install

**Solutions:**

1. **Install system dependencies (Linux):**

   ```bash
   sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2
   ```

2. **Install with dependencies:**

   ```bash
   uv run playwright install --with-deps chromium
   ```

3. **Manual installation:**
   ```bash
   # Download and install manually
   uv run playwright install chromium --force
   ```

## Configuration Issues

### API Key Problems

**Problem:** "No API key found" or authentication errors

**Solutions:**

1. **Verify environment variables:**

   ```bash
   echo $LLM_PROVIDER
   echo $GROQ_API_KEY  # or your chosen provider
   ```

2. **Check .env file:**

   ```bash
   cat .env
   # Ensure no extra spaces or quotes around values
   ```

3. **Test API key:**

   ```bash
   # For Groq
   curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
   ```

4. **Recreate .env file:**
   ```bash
   cp .env.example .env
   # Edit with correct values
   ```

### Provider Configuration Issues

**Problem:** "Unsupported LLM provider" or provider switching failures

**Solutions:**

1. **Check available providers:**

   ```bash
   uv run main.py config get LLM_PROVIDER
   ```

2. **List supported providers:**

   ```bash
   # Supported: openai, azure, groq, anthropic
   export LLM_PROVIDER=groq
   ```

3. **Reset configuration:**
   ```bash
   uv run main.py config reset
   ```

## Browser Connection Issues

### Chrome Launch Failures

**Problem:** Unable to launch Chrome or connect to debugging port

**Solutions:**

1. **Check if Chrome is already running:**

   ```bash
   # Kill existing Chrome processes
   pkill -f chrome
   # or on Windows: taskkill /f /im chrome.exe
   ```

2. **Try different port:**

   ```bash
   uv run main.py launch --port 9223
   ```

3. **Check Chrome installation:**

   ```bash
   # Verify Chrome is installed
   google-chrome --version
   # or
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
   ```

4. **Use headless mode:**
   ```bash
   uv run main.py run --headless
   ```

### Connection Timeout Issues

**Problem:** "Failed to connect to browser" or timeout errors

**Solutions:**

1. **Increase timeout:**

   ```bash
   export DEFAULT_TIMEOUT=60
   uv run main.py run
   ```

2. **Check firewall settings:**

   ```bash
   # Ensure port 9222 (or chosen port) is not blocked
   netstat -an | grep 9222
   ```

3. **Use different connection method:**
   ```bash
   # Launch new browser instead of connecting
   uv run main.py run --profile temp
   ```

### Profile Issues

**Problem:** Browser profile corruption or access denied

**Solutions:**

1. **Use temporary profile:**

   ```bash
   uv run main.py run --profile temp
   ```

2. **Clean profiles:**

   ```bash
   uv run main.py clean --profiles
   ```

3. **Create new profile:**
   ```bash
   uv run main.py profiles create fresh-profile
   uv run main.py run --profile fresh-profile
   ```

## Agent Execution Issues

### Element Not Found Errors

**Problem:** Agent can't find elements on the page

**Solutions:**

1. **Wait for page to load:**

   ```bash
   # Add explicit wait in your task
   "Navigate to example.com, wait 5 seconds, then click the login button"
   ```

2. **Use more specific descriptions:**

   ```bash
   # Instead of: "click button"
   # Use: "click the blue 'Sign In' button in the top right corner"
   ```

3. **Try different element selectors:**

   ```bash
   # If ID doesn't work, try text-based selection
   # The agent will automatically try multiple strategies
   ```

4. **Check if element is in viewport:**
   ```bash
   # Add scrolling to your task
   "Scroll down to find the submit button, then click it"
   ```

### Page Loading Issues

**Problem:** Pages don't load completely or hang

**Solutions:**

1. **Increase page timeout:**

   ```bash
   export PAGE_LOAD_TIMEOUT=60
   ```

2. **Check network connectivity:**

   ```bash
   # Test if site is accessible
   curl -I https://example.com
   ```

3. **Disable images for faster loading:**

   ```python
   # In config.py
   BROWSER_OPTIONS["args"].append("--blink-settings=imagesEnabled=false")
   ```

4. **Use different user agent:**
   ```python
   BROWSER_OPTIONS["args"].append("--user-agent=Mozilla/5.0 (compatible; BrowserAgent)")
   ```

### Task Execution Failures

**Problem:** Agent gets stuck or fails to complete tasks

**Solutions:**

1. **Break down complex tasks:**

   ```bash
   # Instead of one complex task, use multiple simpler ones
   uv run main.py run --task "Navigate to google.com"
   # Then: uv run main.py run --task "Search for 'Python tutorials'"
   ```

2. **Use debug mode:**

   ```bash
   uv run main.py debug --task "your task here"
   ```

3. **Check task phrasing:**

   ```bash
   # Be specific and actionable
   # Good: "Click the red 'Buy Now' button"
   # Bad: "Purchase the item"
   ```

4. **Verify site accessibility:**
   ```bash
   # Some sites block automation - test manually first
   ```

## Performance Issues

### Slow Execution

**Problem:** Agent takes too long to complete tasks

**Solutions:**

1. **Enable fast mode:**

   ```bash
   export FAST_MODE=true
   ```

2. **Use headless mode:**

   ```bash
   uv run main.py run --headless
   ```

3. **Reduce timeouts:**

   ```bash
   export ELEMENT_WAIT_TIMEOUT=5
   export PAGE_LOAD_TIMEOUT=15
   ```

4. **Disable animations:**
   ```python
   # In config.py
   PERFORMANCE_MODE["reduce_transitions"] = True
   ```

### Memory Issues

**Problem:** High memory usage or out of memory errors

**Solutions:**

1. **Close unnecessary browser tabs:**

   ```bash
   # Use fresh profile
   uv run main.py run --profile temp
   ```

2. **Limit concurrent operations:**

   ```bash
   # Avoid running multiple agents simultaneously
   ```

3. **Clear browser cache:**
   ```bash
   uv run main.py clean --cache
   ```

## LLM Provider Issues

### OpenAI Issues

**Problem:** OpenAI API errors or rate limiting

**Solutions:**

1. **Check API quota:**

   ```bash
   # Visit OpenAI dashboard to check usage
   ```

2. **Reduce token usage:**

   ```python
   # In config.py, reduce max_tokens
   LLM_CONFIG["openai"]["max_tokens"] = 1024
   ```

3. **Switch to different model:**
   ```python
   LLM_CONFIG["openai"]["model"] = "gpt-3.5-turbo"
   ```

### Groq Issues

**Problem:** Groq API timeouts or errors

**Solutions:**

1. **Switch models:**

   ```bash
   # Try different Groq model
   export LLM_PROVIDER=groq
   # Edit config.py to use "mixtral-8x7b-32768"
   ```

2. **Check API status:**
   ```bash
   curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY"
   ```

### Azure OpenAI Issues

**Problem:** Azure endpoint or authentication errors

**Solutions:**

1. **Verify endpoint format:**

   ```bash
   # Should be: https://your-resource-name.openai.azure.com/
   echo $AZURE_ENDPOINT
   ```

2. **Check resource name:**

   ```bash
   # Ensure resource name matches your Azure deployment
   ```

3. **Verify API version:**
   ```python
   # In config.py, try different API version
   LLM_CONFIG["azure"]["api_version"] = "2024-02-15-preview"
   ```

## Debug Tools

### Enable Verbose Logging

```bash
export LOG_LEVEL=DEBUG
uv run main.py run --verbose
```

### Capture Screenshots

```python
# In config.py
DEBUG_CONFIG = {
    "screenshot_on_error": True,
    "save_page_source": True
}
```

### Network Debugging

```bash
# Run with network debugging
uv run main.py run --task "your task" --verbose 2>&1 | tee debug.log
```

### Browser Developer Tools

```bash
# Launch with DevTools open
uv run main.py launch --port 9222
# Then navigate to: http://localhost:9222
```

## Getting Help

### System Diagnostics

```bash
# Run comprehensive diagnostics
uv run main.py diagnose --verbose
```

### Check Configuration

```bash
# View current configuration
uv run main.py config get

# Check specific setting
uv run main.py config get LLM_PROVIDER
```

### Version Information

```bash
# Get version and system info
uv run main.py version --detailed
```

### Report Issues

When reporting issues, include:

1. **System information:**

   ```bash
   uv run main.py version --detailed
   ```

2. **Configuration:**

   ```bash
   uv run main.py config get
   ```

3. **Error logs:**

   ```bash
   uv run main.py run --verbose --task "failing task" 2>&1 | tee error.log
   ```

4. **Steps to reproduce:**
   - Exact command used
   - Expected behavior
   - Actual behavior
   - Any error messages

### Community Support

- Check existing issues on GitHub
- Search documentation for similar problems
- Join community discussions
- Provide detailed error information when asking for help
