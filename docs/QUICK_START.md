# 🏃‍♂️ Quick Start Guide

Get up and running with Browser Agent in minutes!

## Basic Usage

### 1. Launch the Browser Agent

```bash
# With uv (recommended)
uv run main.py run

# With python
python main.py run
```

### 2. Enter Your Task

Once the agent is running, you'll see a prompt where you can enter natural language instructions:

```
Enter your instruction: Navigate to google.com and search for 'AI news'
```

### 3. Watch the Magic Happen

The agent will:

1. Open a browser window
2. Navigate to Google
3. Find the search box
4. Type your search query
5. Press enter to search
6. Report back with results

## Basic Commands

### Run with Specific Task

```bash
# Launch with a pre-defined task
uv run main.py run --task "Go to example.com and click the signup button"
```

### Run in Headless Mode

```bash
# Run without visible browser window (for automation)
uv run main.py run --headless
```

### Launch Browser for Manual Control

```bash
# Launch Chrome with debugging enabled for manual use
uv run main.py launch --port 9222
```

### Debug Mode

```bash
# Run with detailed logging for troubleshooting
uv run main.py debug
```

## Example Tasks

Try these example tasks to get familiar with the agent:

### Simple Navigation

```
Navigate to wikipedia.org and search for 'artificial intelligence'
```

### Form Filling

```
Go to httpbin.org/forms/post, fill out the form with test data, and submit it
```

### Information Extraction

```
Visit news.ycombinator.com and tell me the top 3 story headlines
```

### Shopping Assistant

```
Go to Amazon, search for 'wireless headphones', and show me the first three results with their prices
```

## Understanding Agent Responses

The agent will provide detailed feedback about its actions:

```
🔄 Navigating to google.com...
✅ Page loaded successfully
🔍 Analyzing page elements...
📝 Found search box (ID: 3)
⌨️ Typing 'AI news' into search box
🖱️ Clicking search button
✅ Search completed! Found 10 results about AI news
```

## Getting Help

### Command Help

```bash
uv run main.py help
```

### System Diagnostics

```bash
uv run main.py diagnose
```

### Version Information

```bash
uv run main.py version
```

## What's Next?

- 📖 Read the [CLI Reference](CLI_REFERENCE.md) for all available commands
- ⚙️ Check out [Configuration](CONFIGURATION.md) to customize the agent
- 🔧 Learn about [Browser Tools](BROWSER_TOOLS.md) to understand capabilities
- 💡 See [Usage Examples](USAGE_EXAMPLES.md) for more complex scenarios
- 🔍 Visit [Troubleshooting](TROUBLESHOOTING.md) if you encounter issues
