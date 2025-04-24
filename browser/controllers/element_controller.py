"""
Element controller for browser interactions related to finding and interacting with DOM elements.
"""

import re
import asyncio
import random
import json
from langchain_core.tools import tool

from browser.utils.dom_helpers import _parse_click_target, _scroll_element_into_view
from browser.navigation.scroll_manager import scroll

# Global variables
page = None
current_x = 100
current_y = 100

# Import these locally to avoid circular imports
def _import_helpers():
    from browser.utils.input_helpers import (
        natural_mouse_move, update_cursor, click
    )
    return natural_mouse_move, update_cursor, click

async def initialize(browser_page):
    """Initialize the element controller."""
    global page, current_x, current_y
    page = browser_page
    current_x = 100
    current_y = 100
    
    # Initialize cursor position
    natural_mouse_move, update_cursor, _ = _import_helpers()
    await _update_cursor(current_x, current_y)

@tool
async def click(target_description) -> str:
    """
    Simulates a natural human-like click on any webpage element with precise targeting.
    
    This tool intelligently identifies and clicks elements through several methods:
    1. Using element IDs from analyze_page output (most reliable)
    2. Using JSON objects with element properties (highly accurate)
    3. Using natural language descriptions (least precise but most flexible)
    
    The tool handles scrolling elements into view, automatic retries, and employs
    multiple click strategies (selector-based, JavaScript, coordinate-based) to ensure 
    reliable interaction with all types of elements including dynamic content.
    
    Parameters:
        target_description: The element to click, specified as one of:
            - {"id": "5", "type": "button", "text": "Submit"} (most precise)
            - [3][button]Submit (from analyze_page output)
            - "Sign in button" (natural language description)
    
    Returns: Confirmation message or error details if element couldn't be found/clicked.
    """
    try:
        print(f"Attempting visual click for: {target_description}")
        
        # Import page_elements from the analyzer
        from browser.analyzers.page_analyzer import page_elements
        
        # Parse structured input with ID field
        target_id, target_type, target_text, is_structured = _parse_click_target(target_description)
        
        # If ID is provided, try to use it directly from page_elements array
        element = None
        if target_id is not None and page_elements:
            try:
                element_index = int(target_id)
                if 0 <= element_index < len(page_elements):
                    # Direct access to element by ID
                    element = page_elements[element_index]
                    print(f"Using direct element access by ID: {target_id}")
                else:
                    element = None
            except (ValueError, TypeError):
                element = None
        
        # If direct access failed or wasn't available, search in page_elements
        if not element and page_elements:
            print(f"Element ID {target_id} not found, searching in page elements")
            # Search for matching elements in page_elements
            matching_elements = []
            
            for idx, elem in enumerate(page_elements):
                elem_type = elem.get('type', '').lower()
                elem_text = elem.get('text', '').lower() if elem.get('text') else ''
                elem_tag = elem.get('tagName', '').lower()
                
                # Match by type/tag and text if provided
                type_match = False
                if target_type:
                    type_match = (
                        target_type == elem_type or 
                        target_type == elem_tag or
                        (target_type == 'button' and (
                            elem_tag == 'button' or 
                            elem_type == 'button' or 
                            'btn' in (elem.get('className', '') or '')
                        ))
                    )
                else:
                    type_match = True  # No type constraint
                    
                text_match = False
                if target_text:
                    text_match = (
                        target_text.lower() in elem_text or
                        (elem.get('attributes', {}).get('value', '').lower() or '') == target_text.lower() or
                        (elem.get('attributes', {}).get('placeholder', '').lower() or '') == target_text.lower() or
                        (elem.get('attributes', {}).get('aria-label', '').lower() or '') == target_text.lower()
                    )
                else:
                    text_match = True  # No text constraint
                    
                if type_match and text_match:
                    matching_elements.append(elem)
            
            # Prioritize elements that are in viewport and visible
            visible_elements = [e for e in matching_elements if e.get('visible', False) and e.get('inViewport', False)]
            if visible_elements:
                element = visible_elements[0]  # Take the first visible matching element
            elif matching_elements:
                element = matching_elements[0]  # Take any matching element if none visible
        
        # If no element found, try scrolling and searching again
        if not element and page_elements:
            print("No matching element found. Attempting to scroll and search...")
            await scroll("down")
            await asyncio.sleep(1)
            
            # Re-analyze the page after scrolling
            from browser.analyzers.page_analyzer import analyze_page
            await analyze_page()
            
            # Search again in the updated page_elements
            for idx, elem in enumerate(page_elements):
                elem_type = elem.get('type', '').lower()
                elem_text = elem.get('text', '').lower() if elem.get('text') else ''
                elem_tag = elem.get('tagName', '').lower()
                
                # Match by type/tag and text if provided
                type_match = False
                if target_type:
                    type_match = (
                        target_type == elem_type or 
                        target_type == elem_tag or
                        (target_type == 'button' and (
                            elem_tag == 'button' or 
                            elem_type == 'button' or 
                            'btn' in (elem.get('className', '') or '')
                        ))
                    )
                else:
                    type_match = True  # No type constraint
                    
                text_match = False
                if target_text:
                    text_match = (
                        target_text.lower() in elem_text or
                        (elem.get('attributes', {}).get('value', '').lower() or '') == target_text.lower() or
                        (elem.get('attributes', {}).get('placeholder', '').lower() or '') == target_text.lower() or
                        (elem.get('attributes', {}).get('aria-label', '').lower() or '') == target_text.lower()
                    )
                else:
                    text_match = True  # No text constraint
                    
                if type_match and text_match:
                    element = elem
                    break
        
        # If still no matching element, return error
        if not element:
            if is_structured:
                criteria = [f"{k}={v}" for k, v in {'id': target_id, 'type': target_type, 'text': target_text}.items() if v]
                return f"No elements matching {', '.join(criteria)} found, even after scrolling."
            else:
                return f"No elements matching '{target_description}' found, even after scrolling."
        
        print(f"Selected element: ID={element.get('id', 'unknown')}, Type={element['type']}, Text=\"{element['text']}\"")
        
        # Ensure element is visible in viewport (scroll if needed)
        if not element.get('inViewport', False):
            await _scroll_element_into_view(element)
        
        # Move cursor to element for visual feedback before clicking
        x, y = element['center_x'], element['center_y']
        await _natural_mouse_move(x, y)
        
        # Perform click
        result = await _click(x, y)
        
        return f"Clicked on element: {element['type']} with text '{element['text']}'"
        
    except Exception as e:
        print(f"Error in click: {str(e)}")
        return f"Error clicking on element: {str(e)}"

@tool
async def fill_input(json_input):
    """
    Fills an input field with text without clicking first.
    
    Parameters:
        json_input: JSON with target and value info
        {
            "id": "5",                 # Element ID (required)
            "type": "input",           # Element type (required)
            "text": "Email",           # Description (required)
            "value": "user@example.com" # Text to fill (required)
        }
        
    Returns: Result of the fill operation
    """
    try:
        # Parse the JSON input
        print(f"Received JSON input: {json_input}")
        
        if isinstance(json_input, str):
            import json
            try:
                input_data = json.loads(json_input)
            except json.JSONDecodeError:
                # If not valid JSON, try to parse as a Python dictionary string
                try:
                    # Convert single quotes to double quotes for proper JSON format
                    formatted_input = json_input.replace("'", "\"")
                    input_data = json.loads(formatted_input)
                except:
                    return "Error: Invalid JSON input format. Please provide a valid JSON string."
        else:
            input_data = json_input
        
        # Extract values from the input
        target_id = input_data.get("id")
        target_type = input_data.get("type")
        target_text = input_data.get("text")
        value = input_data.get("value")
        
        if not value:
            return "Error: 'value' field is required in the input JSON."
            
        # Create a target description that works with the existing parsing logic
        if target_id:
            target_description = {"id": target_id, "type": target_type, "text": target_text}
        elif target_type and target_text:
            target_description = {"type": target_type, "text": target_text}
        elif target_text:
            target_description = target_text
        else:
            return "Error: At least one of 'id', 'type', or 'text' must be provided to identify the element."
        
        # Import page_elements from the analyzer
        from browser.analyzers.page_analyzer import page_elements
        
        # Parse structured input with ID field
        parsed_id, parsed_type, parsed_text, is_structured = _parse_click_target(target_description)
        
        # If ID is provided, try to use it directly from page_elements array
        element = None
        if parsed_id is not None and page_elements:
            try:
                element_index = int(parsed_id)
                if 0 <= element_index < len(page_elements):
                    # Direct access to element by ID
                    element = page_elements[element_index]
                    print(f"Using direct element access by ID: {parsed_id}")
                else:
                    element = None
            except (ValueError, TypeError):
                element = None
    
        
        # If still no matching element, return error
        if not element:
            if is_structured:
                criteria = [f"{k}={v}" for k, v in {'id': parsed_id, 'type': parsed_type, 'text': parsed_text}.items() if v]
                return f"No input field matching {', '.join(criteria)} found, even after scrolling."
            else:
                return f"No input field matching '{target_description}' found, even after scrolling."
        
        print(f"Selected input field: ID={element.get('id', 'unknown')}, Type={element['type']}, Text=\"{element['text']}\"")
        
        # Ensure element is visible in viewport (scroll if needed)
        if not element.get('inViewport', False):
            await _scroll_element_into_view(element)
            await asyncio.sleep(0.8)  # Wait for scroll to complete
        
        # Get the selector for the element
        selector = element.get('cssSelector')
        
        if not selector:
            return f"Could not determine a valid selector for element: {element['type']} with text '{element['text']}'"
        
        # Use DOM manipulation directly to fill the input field instead of page.fill
        try:
            # Fill the input field using direct DOM manipulation
            fill_result = await page.evaluate("""
                (params) => {
                    const { selector, value } = params;
                    try {
                        const element = document.querySelector(selector);
                        if (!element) {
                            return { success: false, error: 'Element not found with selector' };
                        }
                        
                        // Handle focus and ensure element is visible
                        if (document.activeElement) {
                            document.activeElement.blur();
                        }
                        
                        // Different handling based on element type
                        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                            // Clear the field first
                            element.value = '';
                            
                            // Focus the element (important for some form validation)
                            element.focus();
                            
                            // Set the value using property descriptor if available (for custom inputs)
                            const originalValueSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
                            if (originalValueSetter) {
                                originalValueSetter.call(element, value);
                            } else {
                                // Fallback to direct assignment
                                element.value = value;
                            }
                            
                            // Trigger necessary events to ensure form validation works
                            element.dispatchEvent(new Event('input', { bubbles: true }));
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                            
                            // For inputs that use keydown/keyup events
                            // Simulate typing by dispatching keyboard events for each character
                            for (let i = 0; i < value.length; i++) {
                                const char = value[i];
                                
                                // Special handling for newline characters
                                if (char === '\\n') {
                                    // Dispatch Enter key events for newlines
                                    element.dispatchEvent(new KeyboardEvent('keydown', {
                                        key: 'Enter',
                                        code: 'Enter',
                                        keyCode: 13,
                                        bubbles: true
                                    }));
                                    
                                    element.dispatchEvent(new KeyboardEvent('keypress', {
                                        key: 'Enter',
                                        code: 'Enter',
                                        keyCode: 13,
                                        bubbles: true
                                    }));
                                    
                                    element.dispatchEvent(new KeyboardEvent('keyup', {
                                        key: 'Enter',
                                        code: 'Enter',
                                        keyCode: 13,
                                        bubbles: true
                                    }));
                                } else {
                                    // Regular character handling
                                    // Key down event
                                    element.dispatchEvent(new KeyboardEvent('keydown', {
                                        key: char,
                                        code: 'Key' + char.toUpperCase(),
                                        bubbles: true
                                    }));
                                    
                                    // Key press event
                                    element.dispatchEvent(new KeyboardEvent('keypress', {
                                        key: char,
                                        code: 'Key' + char.toUpperCase(),
                                        bubbles: true
                                    }));
                                    
                                    // Key up event
                                    element.dispatchEvent(new KeyboardEvent('keyup', {
                                        key: char,
                                        code: 'Key' + char.toUpperCase(),
                                        bubbles: true
                                    }));
                                }
                            }
                            
                            // Don't blur at the end - keep the element focused
                            // element.blur();
                            
                            return { success: true, method: 'dom_manipulation' };
                        } else if (element.isContentEditable) {
                            // Handle contentEditable elements (rich text editors)
                            element.focus();
                            
                            // Use a safer approach for setting content
                            try {
                                document.execCommand('selectAll', false, null);
                                document.execCommand('delete', false, null);
                                
                                // Insert text considering newlines
                                const lines = value.split('\\n');
                                for (let i = 0; i < lines.length; i++) {
                                    if (i > 0) {
                                        document.execCommand('insertParagraph', false);
                                    }
                                    document.execCommand('insertText', false, lines[i]);
                                }
                                
                                element.dispatchEvent(new Event('input', { bubbles: true }));
                                // Don't blur the element to keep it focused
                                // element.blur();
                                return { success: true, method: 'contentEditable' };
                            } catch (innerError) {
                                return { success: false, error: 'Failed to set content: ' + innerError.toString() };
                            }
                        } else {
                            return { success: false, error: 'Unsupported element type: ' + element.tagName };
                        }
                    } catch (error) {
                        return { success: false, error: error.toString() };
                    }
                }
            """, { 'selector': selector, 'value': value })
            
            if not fill_result.get('success'):
                print(f"DOM fill failed: {fill_result.get('error')}. Trying fallback method.")
                # Fallback to standard Playwright fill method
                await page.fill(selector, value)
                
            
            return f"Filled input field: {element['type']} with text '{element['text']}' with value: '{value}'"
        except Exception as e:
            print(f"Error in DOM fill, using fallback: {e}")
            try:
                # Last resort - use standard Playwright fill
                await page.fill(selector, value)
                return f"Filled input field: {element['type']} with text '{element['text']}' with value: '{value}' (using fallback)"
            except Exception as fill_err:
                print(f"All filling methods failed: {fill_err}")
                return f"Error filling input field: {str(e)}"
    except Exception as e:
        print(f"Error in fill_input: {str(e)}")
        return f"Error filling input field: {str(e)}"

@tool
async def select_option(json_input):
    """
    Selects an option from a dropdown/select element.
    
    Parameters:
        json_input: JSON with target and value info
        {
            "id": "5",              # Element ID (required)
            "type": "dropdown",     # Element type (required)
            "text": "Country",      # Description (required)
            "value": "USA"          # Option to select (required)
        }
        
    Returns: Result of the select operation
    """
    try:
        # Parse the JSON input
        print(f"Received JSON input: {json_input}")
        
        if isinstance(json_input, str):
            import json
            try:
                input_data = json.loads(json_input)
            except json.JSONDecodeError:
                # If not valid JSON, try to parse as a Python dictionary string
                try:
                    # Convert single quotes to double quotes for proper JSON format
                    formatted_input = json_input.replace("'", "\"")
                    input_data = json.loads(formatted_input)
                except:
                    return "Error: Invalid JSON input format. Please provide a valid JSON string."
        else:
            input_data = json_input
        
        # Extract values from the input
        target_id = input_data.get("id")
        target_type = input_data.get("type")
        target_text = input_data.get("text")
        option_value = input_data.get("value")
        
        if not option_value:
            return "Error: 'value' field is required in the input JSON."
            
        # Create a target description that works with the existing parsing logic
        if target_id:
            target_description = {"id": target_id, "type": target_type, "text": target_text}
        elif target_type and target_text:
            target_description = {"type": target_type, "text": target_text}
        elif target_text:
            target_description = target_text
        else:
            return "Error: At least one of 'id', 'type', or 'text' must be provided to identify the element."
        
        print(f"Attempting to select option '{option_value}' from dropdown: {target_description}")
        
        # Import page_elements from the analyzer
        from browser.analyzers.page_analyzer import page_elements
        
        # Parse structured input with ID field
        parsed_id, parsed_type, parsed_text, is_structured = _parse_click_target(target_description)
        
        # If ID is provided, try to use it directly from page_elements array
        element = None
        if parsed_id is not None and page_elements:
            try:
                element_index = int(parsed_id)
                if 0 <= element_index < len(page_elements):
                    # Direct access to element by ID
                    element = page_elements[element_index]
                    print(f"Using direct element access by ID: {parsed_id}")
                else:
                    element = None
            except (ValueError, TypeError):
                element = None
        
        # If direct access failed or wasn't available, search in page_elements
        if not element and page_elements:
            print(f"Element ID {parsed_id} not found, searching in page elements")
            # Search for matching elements in page_elements
            matching_elements = []
            
            for idx, elem in enumerate(page_elements):
                elem_type = elem.get('type', '').lower()
                elem_text = elem.get('text', '').lower() if elem.get('text') else ''
                elem_tag = elem.get('tagName', '').lower()
                
                # Match by type/tag and text if provided
                type_match = False
                if parsed_type:
                    type_match = (
                        parsed_type == elem_type or 
                        parsed_type == elem_tag or
                        (parsed_type == 'dropdown' and (
                            elem_tag == 'select' or 
                            elem_type == 'dropdown' or 
                            elem.get('attributes', {}).get('role', '') == 'listbox'
                        ))
                    )
                else:
                    type_match = True  # No type constraint
                    
                text_match = False
                if parsed_text:
                    text_match = (
                        parsed_text.lower() in elem_text or
                        (elem.get('attributes', {}).get('value', '').lower() or '') == parsed_text.lower() or
                        (elem.get('attributes', {}).get('placeholder', '').lower() or '') == parsed_text.lower() or
                        (elem.get('attributes', {}).get('aria-label', '').lower() or '') == parsed_text.lower()
                    )
                else:
                    text_match = True  # No text constraint
                    
                if type_match and text_match:
                    matching_elements.append(elem)
            
            # Prioritize elements that are in viewport and visible
            visible_elements = [e for e in matching_elements if e.get('visible', False) and e.get('inViewport', False)]
            if visible_elements:
                element = visible_elements[0]  # Take the first visible matching element
            elif matching_elements:
                element = matching_elements[0]  # Take any matching element if none visible
        
        # If no element found, try scrolling and searching again
        if not element and page_elements:
            print("No matching element found. Attempting to scroll and search...")
            await scroll("down")
            await asyncio.sleep(1)
            
            # Re-analyze the page after scrolling
            from browser.analyzers.page_analyzer import analyze_page
            await analyze_page()
            
            # Search again in the updated page_elements
            for idx, elem in enumerate(page_elements):
                elem_type = elem.get('type', '').lower()
                elem_text = elem.get('text', '').lower() if elem.get('text') else ''
                elem_tag = elem.get('tagName', '').lower()
                
                # Match by type/tag and text if provided
                type_match = False
                if parsed_type:
                    type_match = (
                        parsed_type == elem_type or 
                        parsed_type == elem_tag or
                        (parsed_type == 'dropdown' and (
                            elem_tag == 'select' or 
                            elem_type == 'dropdown' or 
                            elem.get('attributes', {}).get('role', '') == 'listbox'
                        ))
                    )
                else:
                    type_match = True  # No type constraint
                    
                text_match = False
                if parsed_text:
                    text_match = (
                        parsed_text.lower() in elem_text or
                        (elem.get('attributes', {}).get('value', '').lower() or '') == parsed_text.lower() or
                        (elem.get('attributes', {}).get('placeholder', '').lower() or '') == parsed_text.lower() or
                        (elem.get('attributes', {}).get('aria-label', '').lower() or '') == parsed_text.lower()
                    )
                else:
                    text_match = True  # No text constraint
                    
                if type_match and text_match:
                    element = elem
                    break
        
        # If still no matching element, return error
        if not element:
            if is_structured:
                criteria = [f"{k}={v}" for k, v in {'id': parsed_id, 'type': parsed_type, 'text': parsed_text}.items() if v]
                return f"No dropdown matching {', '.join(criteria)} found, even after scrolling."
            else:
                return f"No dropdown matching '{target_description}' found, even after scrolling."
        
        print(f"Selected dropdown: ID={element.get('id', 'unknown')}, Type={element['type']}, Text=\"{element['text']}\"")
        
        # Ensure element is visible in viewport (scroll if needed)
        if not element.get('inViewport', False):
            await _scroll_element_into_view(element)
            await asyncio.sleep(0.8)  # Wait for scroll to complete
        
        # Get the selector for the element
        selector = element.get('cssSelector')
        
        if not selector:
            return f"Could not determine a valid selector for dropdown: {element['type']} with text '{element['text']}'"
        
        # Rest of the function remains the same...
        # For select elements, we can use the built-in select_option method
        if element['type'] == 'dropdown' or element['tagName'].lower() == 'select':
            # Try selecting by label text first, then by value
            try:
                # Try to select by visible text
                await page.select_option(selector, label=option_value)
                return f"Selected option '{option_value}' from dropdown: {element['text']} by visible text"
            except Exception as e1:
                try:
                    # If that fails, try selecting by value attribute
                    await page.select_option(selector, value=option_value)
                    return f"Selected option with value '{option_value}' from dropdown: {element['text']}"
                except Exception as e2:
                    try:
                        # Last try: by index if it's a number
                        if option_value.isdigit():
                            await page.select_option(selector, index=int(option_value))
                            return f"Selected option at index {option_value} from dropdown: {element['text']}"
                        else:
                            raise Exception(f"Could not select option by text or value: {e1}, {e2}")
                    except Exception as e3:
                        return f"Failed to select option '{option_value}' from dropdown: {str(e3)}"
        else:
            # For non-standard dropdowns (like custom UI components), use the click approach
            # First click on the dropdown to open it
            x, y = element['center_x'], element['center_y']
            await _natural_mouse_move(x, y)
            await _click(x, y)
            await asyncio.sleep(1)  # Wait for dropdown to open
            
            # Then try to find and click the option
            option_element = await page.evaluate('''
                (optionText) => {
                    // First try matching by exact text
                    const options = Array.from(document.querySelectorAll('li, div[role="option"], option, .dropdown-item'));
                    
                    // Find by text content
                    let foundOption = options.find(el => 
                        el.innerText.trim() === optionText || 
                        el.textContent.trim() === optionText ||
                        el.getAttribute('value') === optionText
                    );
                    
                    // If not found, try a more relaxed search
                    if (!foundOption) {
                        foundOption = options.find(el => 
                            el.innerText.trim().includes(optionText) || 
                            el.textContent.trim().includes(optionText)
                        );
                    }
                    
                    if (foundOption) {
                        const rect = foundOption.getBoundingClientRect();
                        return {
                            x: rect.left + rect.width/2 + window.pageXOffset,
                            y: rect.top + rect.height/2 + window.pageYOffset,
                            text: foundOption.innerText.trim() || foundOption.textContent.trim()
                        };
                    }
                    
                    return null;
                }
            ''', option_value)
            
            if option_element:
                # Click on the option
                await _natural_mouse_move(option_element['x'], option_element['y'])
                await _click(option_element['x'], option_element['y'])
                return f"Clicked on option '{option_element['text']}' in dropdown: {element['text']}"
            else:
                return f"Could not find option '{option_value}' in the opened dropdown: {element['text']}"
        
    except Exception as e:
        print(f"Error in select_option: {str(e)}")
        return f"Error selecting option from dropdown: {str(e)}"

# Helper methods
async def _click(x, y):
    """Click with the cursor."""
    _, _, click = _import_helpers()
    await click(page, x, y)

async def _natural_mouse_move(target_x, target_y):
    """Move the virtual mouse in a natural way, simulating human movement."""
    global current_x, current_y
    
    # Get starting position
    start_x = current_x
    start_y = current_y
    
    # Get helpers
    natural_mouse_move, _, _ = _import_helpers()
    
    # Get path points
    path_points = await natural_mouse_move(
        page, start_x, start_y, target_x, target_y
    )
    
    # Execute the movement
    for x, y in path_points:
        await _update_cursor(x, y)
        
        # Slight delay between movements with variable timing
        await asyncio.sleep(0.01 + random.uniform(0, 0.02))
        
        # Occasionally pause briefly (simulating human hesitation)
        if (random.random() < 0.05):  # 5% chance
            await asyncio.sleep(random.uniform(0.1, 0.3))
    
    # Update final position
    current_x = target_x
    current_y = target_y

async def _update_cursor(x, y):
    """Update the virtual cursor position."""
    global current_x, current_y
    current_x = x
    current_y = y
    
    # Get update_cursor helper
    _, update_cursor, _ = _import_helpers()
    await update_cursor(page, x, y)

async def _handle_new_tab(popup):
    """Handle new tab popup events by getting URL and navigating in main tab instead."""
    try:
        # Wait briefly for the popup to initialize
        await asyncio.sleep(0.5)
        # Get the URL of the popup
        popup_url = popup.url
        if (popup_url and popup_url != "about:blank"):
            # Close the popup
            await popup.close()
            # Navigate the main page to that URL instead
            await page.goto(popup_url)
            print(f"Redirected popup to main tab: {popup_url}")
    except Exception as e:
        print(f"Error handling popup: {e}")
        # Try to close the popup anyway
        try:
            await popup.close()
        except:
            pass
