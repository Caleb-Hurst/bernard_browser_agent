# 🛠️ Browser Tools Reference

Complete reference for all browser automation tools available to the AI agent.

## Core Analysis Tools

### `analyze_page`

Scans the current page's DOM to create a map of all interactive elements with numbered IDs.

**Usage:**

```python
analyze_page()
```

**Returns:**

- Numbered list of all interactive elements
- Element types (button, link, input, etc.)
- Element text content
- Element attributes and properties

**Example Output:**

```
[1][button]Sign Up
[2][link]Learn More
[3][input]Email Address (placeholder: Enter your email)
[4][select]Country
[5][checkbox]I agree to terms
```

**When to Use:**

- After navigating to a new page
- After page content changes dynamically
- Before attempting to interact with elements
- When element IDs have changed

## Navigation Tools

### `navigate`

Navigate to a specific URL.

**Usage:**

```python
navigate("https://example.com")
```

**Parameters:**

- `url` (string): The URL to navigate to

**Features:**

- Automatic protocol detection (adds https:// if missing)
- Waits for page to fully load
- Handles redirects automatically
- Returns navigation status

### `go_back`

Navigate to the previous page in browser history.

**Usage:**

```python
go_back()
```

**Features:**

- Works like the browser's back button
- Maintains page state
- Handles history availability

### `scroll`

Scroll the page viewport in specified directions.

**Usage:**

```python
scroll("down")    # Scroll down
scroll("up")      # Scroll up
scroll("top")     # Scroll to top
scroll("bottom")  # Scroll to bottom
```

**Parameters:**

- `direction` (string): "up", "down", "top", "bottom"

**Features:**

- Detects scroll boundaries
- Returns feedback about scroll limits
- Smooth scrolling animation

## Element Interaction Tools

### `click`

Click on elements using various identification methods.

**Usage:**

```python
# Using element ID from analyze_page
click("[3][button]Submit")

# Using JSON object
click({"id": "3", "type": "button", "text": "Submit"})

# Using natural language
click("Submit button")
```

**Parameters:**

- `target_description`: Element identifier (ID, JSON object, or description)

**Features:**

- Multiple identification strategies
- Automatic scrolling to element
- Visibility verification
- Retry mechanisms on failure

### `type`

Types text into the currently focused element.

**Usage:**

```python
type("Hello, World!")
```

**Parameters:**

- `value` (string): Text to type

**Features:**

- Clears existing text first (Ctrl+A/Cmd+A)
- Natural typing simulation
- Works with any text input element

**Workflow:**

1. Click on input field to focus it
2. Use `type()` to enter text

### `select_option`

Select options from dropdown menus and select elements.

**Usage:**

```python
select_option({
    "id": "5",
    "type": "dropdown",
    "text": "Country",
    "value": "USA"
})
```

**Parameters:**

- `json_input`: JSON object with target and value information

**JSON Format:**

```json
{
  "id": "element_id",
  "type": "dropdown",
  "text": "element_description",
  "value": "option_to_select"
}
```

**Features:**

- Works with standard HTML `<select>` elements
- Handles custom dropdown components
- Multiple selection strategies (by text, value, index)

### `keyboard_action`

Send keyboard shortcuts and special keys.

**Usage:**

```python
keyboard_action("Enter")     # Press Enter
keyboard_action("Tab")       # Press Tab
keyboard_action("Escape")    # Press Escape
keyboard_action("Ctrl+A")    # Select all
keyboard_action("Ctrl+C")    # Copy
keyboard_action("Ctrl+V")    # Paste
```

**Common Key Combinations:**

- `Enter` - Submit forms, confirm actions
- `Tab` - Navigate between form fields
- `Escape` - Close dialogs, cancel actions
- `Ctrl+A` / `Cmd+A` - Select all text
- `Ctrl+C` / `Cmd+C` - Copy
- `Ctrl+V` / `Cmd+V` - Paste
- `Ctrl+Z` / `Cmd+Z` - Undo

## User Interaction Tools

### `ask_user`

Request information from the user during task execution.

**Usage:**

```python
# Text input
ask_user({
    "prompt": "Please enter your username",
    "type": "text"
})

# Password input (hidden)
ask_user({
    "prompt": "Please enter your password",
    "type": "password"
})

# Multiple choice
ask_user({
    "prompt": "Choose your preferred option",
    "type": "choice",
    "choices": ["Option A", "Option B", "Option C"]
})
```

**Parameters:**

- `json_input`: JSON object with prompt configuration

**JSON Format:**

```json
{
  "prompt": "Question or instruction text",
  "type": "text|password|choice",
  "choices": ["array", "of", "options"] // Only for choice type
}
```

## Element Identification Strategies

### Using Element IDs

Most reliable method using IDs from `analyze_page`:

```python
# First, analyze the page
analyze_page()

# Then use the numbered ID
click("[3][button]Submit")
```

### Using JSON Objects

Structured approach with multiple identifiers:

```python
click({
    "id": "3",
    "type": "button",
    "text": "Submit"
})
```

### Using Natural Language

Flexible but less precise:

```python
click("blue submit button at the bottom")
```

## Best Practices

### Element Interaction Workflow

1. **Analyze First**: Always call `analyze_page()` when arriving at a new page
2. **Use IDs When Possible**: Element IDs are most reliable
3. **Verify Actions**: Re-analyze after significant page changes
4. **Handle Dynamics**: Some pages change element IDs frequently

### Form Filling Workflow

```python
# 1. Analyze the page
analyze_page()

# 2. Click on input field to focus
click("[3][input]Email")

# 3. Type the value
type("user@example.com")

# 4. Move to next field
click("[4][input]Password")
type("mypassword")

# 5. Submit form
click("[5][button]Submit")
```

### Error Handling

- If element not found, try scrolling and re-analyzing
- Use more specific descriptions if multiple elements match
- Try alternative selection methods (text vs ID)

### Performance Tips

- Minimize `analyze_page()` calls - only when necessary
- Group related actions together
- Use element IDs instead of descriptions when possible
- Take advantage of automatic scrolling and waiting

## Advanced Features

### Dynamic Content

The tools handle dynamic content by:

- Waiting for elements to become visible
- Re-scanning after content changes
- Automatic retries with different strategies

### Multiple Element Matches

When multiple elements match:

- Prioritizes visible elements in viewport
- Uses first visible match
- Falls back to first overall match

### Error Recovery

Built-in error recovery includes:

- Automatic scrolling to find elements
- Alternative selection strategies
- Graceful degradation with helpful error messages

## Debugging Tools

### Verbose Element Information

Enable detailed element information:

```python
# Set in configuration
DEBUG_CONFIG = {
    "verbose_element_info": True
}
```

### Screenshot on Error

Capture screenshots when errors occur:

```python
DEBUG_CONFIG = {
    "screenshot_on_error": True
}
```

### Page Source Saving

Save HTML source for debugging:

```python
DEBUG_CONFIG = {
    "save_page_source": True
}
```
