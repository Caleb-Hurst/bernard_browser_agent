# 🎯 CLI Reference

Complete reference for all Browser Agent command-line interface commands.

## Core Commands

### `run` - Execute AI Agent

Run the AI agent with interactive or predefined tasks.

```bash
uv run main.py run [OPTIONS]
```

**Options:**

- `--task TEXT` - Specify a task to execute immediately
- `--headless` - Run in headless mode (no visible browser)
- `--profile TEXT` - Use a specific browser profile
- `--verbose` - Enable verbose logging
- `--timeout INTEGER` - Set timeout for operations (seconds)

**Examples:**

```bash
# Interactive mode
uv run main.py run

# With specific task
uv run main.py run --task "Navigate to google.com"

# Headless mode
uv run main.py run --headless --task "Check if example.com is online"

# With custom profile
uv run main.py run --profile my-profile --task "Login to my account"
```

### `launch` - Launch Browser

Launch Chrome with debugging enabled for manual control or agent connection.

```bash
uv run main.py launch [OPTIONS]
```

**Options:**

- `--port INTEGER` - Debug port (default: 9222)
- `--profile TEXT` - Browser profile to use
- `--headless` - Launch in headless mode
- `--user-data-dir TEXT` - Custom user data directory

**Examples:**

```bash
# Launch with default settings
uv run main.py launch

# Custom debug port
uv run main.py launch --port 9223

# With specific profile
uv run main.py launch --profile work-profile

# Temporary profile
uv run main.py launch --profile temp
```

### `connect` - Connect to Existing Browser

Connect to an already running Chrome instance with debugging enabled.

```bash
uv run main.py connect [OPTIONS]
```

**Options:**

- `--port INTEGER` - Debug port to connect to (default: 9222)
- `--host TEXT` - Host address (default: localhost)
- `--timeout INTEGER` - Connection timeout (default: 10)

**Examples:**

```bash
# Connect to default port
uv run main.py connect

# Connect to custom port
uv run main.py connect --port 9223

# Connect to remote instance
uv run main.py connect --host 192.168.1.100 --port 9222
```

## Profile Management

### `profiles list` - List Profiles

Show all available browser profiles.

```bash
uv run main.py profiles list
```

### `profiles create` - Create Profile

Create a new browser profile.

```bash
uv run main.py profiles create [OPTIONS] PROFILE_NAME
```

**Options:**

- `--description TEXT` - Profile description
- `--copy-from TEXT` - Copy settings from existing profile

**Examples:**

```bash
# Create basic profile
uv run main.py profiles create work-profile

# With description
uv run main.py profiles create --description "Work browsing profile" work-profile

# Copy from existing
uv run main.py profiles create --copy-from default work-profile
```

### `profiles remove` - Remove Profile

Remove an existing browser profile.

```bash
uv run main.py profiles remove [OPTIONS] PROFILE_NAME
```

**Options:**

- `--force` - Force removal without confirmation

**Examples:**

```bash
# Remove with confirmation
uv run main.py profiles remove old-profile

# Force removal
uv run main.py profiles remove --force temp-profile
```

### `profiles info` - Profile Information

Get detailed information about a specific profile.

```bash
uv run main.py profiles info PROFILE_NAME
```

## System & Diagnostics

### `diagnose` - System Diagnostics

Run comprehensive system diagnostics to check configuration and dependencies.

```bash
uv run main.py diagnose [OPTIONS]
```

**Options:**

- `--verbose` - Show detailed diagnostic information
- `--fix` - Attempt to fix common issues automatically

**Examples:**

```bash
# Basic diagnostics
uv run main.py diagnose

# Detailed diagnostics
uv run main.py diagnose --verbose

# Try to fix issues
uv run main.py diagnose --fix
```

### `clean` - Clean Temporary Files

Clean temporary files, profiles, and browser data.

```bash
uv run main.py clean [OPTIONS]
```

**Options:**

- `--profiles` - Clean temporary profiles only
- `--cache` - Clean browser cache
- `--all` - Clean everything
- `--dry-run` - Show what would be cleaned without doing it

**Examples:**

```bash
# Clean temporary files
uv run main.py clean

# Clean only profiles
uv run main.py clean --profiles

# See what would be cleaned
uv run main.py clean --dry-run --all
```

### `version` - Version Information

Show version and system information.

```bash
uv run main.py version [OPTIONS]
```

**Options:**

- `--detailed` - Show detailed system information

## Configuration

### `config set` - Set Configuration

Set configuration values.

```bash
uv run main.py config set KEY VALUE
```

**Examples:**

```bash
# Set LLM provider
uv run main.py config set LLM_PROVIDER groq

# Set browser headless mode
uv run main.py config set BROWSER_HEADLESS true

# Set timeout
uv run main.py config set DEFAULT_TIMEOUT 30
```

### `config get` - Get Configuration

Get configuration values.

```bash
uv run main.py config get [KEY]
```

**Examples:**

```bash
# Get all configuration
uv run main.py config get

# Get specific key
uv run main.py config get LLM_PROVIDER
```

### `config reset` - Reset Configuration

Reset configuration to default values.

```bash
uv run main.py config reset [OPTIONS]
```

**Options:**

- `--confirm` - Skip confirmation prompt

## Help & Debug

### `help` - Show Help

Show comprehensive help information.

```bash
uv run main.py help [COMMAND]
```

**Examples:**

```bash
# General help
uv run main.py help

# Help for specific command
uv run main.py help run
```

### `debug` - Debug Mode

Enable debug mode for troubleshooting.

```bash
uv run main.py debug [OPTIONS]
```

**Options:**

- `--log-level TEXT` - Set log level (DEBUG, INFO, WARNING, ERROR)
- `--log-file TEXT` - Log to file instead of console

## Global Options

These options work with most commands:

- `--verbose` - Enable verbose output
- `--quiet` - Suppress non-error output
- `--config TEXT` - Use custom configuration file
- `--no-color` - Disable colored output

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - Browser connection error
- `4` - Task execution error
- `130` - Interrupted by user (Ctrl+C)

## Environment Variables

Commands can be influenced by these environment variables:

- `LLM_PROVIDER` - Default LLM provider
- `BROWSER_HEADLESS` - Default headless mode
- `DEFAULT_TIMEOUT` - Default operation timeout
- `LOG_LEVEL` - Default logging level
