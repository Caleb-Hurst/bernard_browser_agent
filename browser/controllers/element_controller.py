"""
Element controller for browser interactions related to finding and interacting with DOM elements.
"""

import re
import time
import json
from langchain_core.tools import tool

from browser.utils.dom_helpers import _parse_click_target
from browser.navigation.scroll_manager import scroll

# Global variables
page = None
current_x = 100
current_y = 100

# Import these locally to avoid circular imports
def _import_helpers():
    from browser.utils.input_helpers import (
        update_cursor, click
    )
    return update_cursor, click

def initialize(browser_page):
    """Initialize the element controller."""
    global page, current_x, current_y
    page = browser_page
    current_x = 100
    current_y = 100
    
    # Initialize cursor position
    update_cursor, _ = _import_helpers()
    _update_cursor(current_x, current_y)

@tool
def click(target_description) -> str:
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
            scroll("down")
            
            # Re-analyze the page after scrolling
            from browser.analyzers.page_analyzer import analyze_page
            analyze_page()
            
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
        
        # Move cursor to element for visual feedback before clicking
        x, y = element['center_x'], element['center_y']
        _update_cursor(x, y)
        
        # Perform click
        result = _click(x, y)
        
        return f"Clicked on element: {element['type']} with text '{element['text']}'"
        
    except Exception as e:
        print(f"Error in click: {str(e)}")
        return f"Error clicking on element: {str(e)}"


@tool
def type(value):
    """
    Types text into the currently focused element using keyboard simulation.
    
    Parameters:
        value: The text to type
        
    Returns: Result of the typing operation
    """
    try:
        print(f"Typing value: {value}")
        
        if not value:
            return "Error: 'value' parameter is required."
        
        print("Typing into currently focused element")
        
        page.keyboard.type(value)
        
        print(f"Successfully typed value using keyboard")
        return f"Typed '{value}' into currently focused element"
    
    except Exception as e:
        print(f"Error in type: {str(e)}")
        return f"Error typing: {str(e)}"

@tool
def select_option(json_input):
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
            scroll("down")
            
            # Re-analyze the page after scrolling
            from browser.analyzers.page_analyzer import analyze_page
            analyze_page()
            
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
                page.select_option(selector, label=option_value)
                return f"Selected option '{option_value}' from dropdown: {element['text']} by visible text"
            except Exception as e1:
                try:
                    # If that fails, try selecting by value attribute
                    page.select_option(selector, value=option_value)
                    return f"Selected option with value '{option_value}' from dropdown: {element['text']}"
                except Exception as e2:
                    try:
                        # Last try: by index if it's a number
                        if option_value.isdigit():
                            page.select_option(selector, index=int(option_value))
                            return f"Selected option at index {option_value} from dropdown: {element['text']}"
                        else:
                            raise Exception(f"Could not select option by text or value: {e1}, {e2}")
                    except Exception as e3:
                        return f"Failed to select option '{option_value}' from dropdown: {str(e3)}"
        else:
            # For non-standard dropdowns (like custom UI components), use the click approach
            # First click on the dropdown to open it
            x, y = element['center_x'], element['center_y']
            _update_cursor(x, y)
            _click(x, y)
            # Minimal wait for dropdown to open
            time.sleep(0.1)
            
            # Then try to find and click the option
            option_element = page.evaluate('''
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
                _update_cursor(option_element['x'], option_element['y'])
                _click(option_element['x'], option_element['y'])
                return f"Clicked on option '{option_element['text']}' in dropdown: {element['text']}"
            else:
                return f"Could not find option '{option_value}' in the opened dropdown: {element['text']}"
        
    except Exception as e:
        print(f"Error in select_option: {str(e)}")
        return f"Error selecting option from dropdown: {str(e)}"

# Helper methods
def _click(x, y):
    """Click with the cursor."""
    _, click = _import_helpers()
    click(page, x, y)

def _update_cursor(target_x, target_y):
    """Update the virtual cursor position directly."""
    global current_x, current_y
    
    # Update position directly without animation
    current_x = target_x
    current_y = target_y
    
    # Get update_cursor helper
    update_cursor, _ = _import_helpers()
    update_cursor(page, target_x, target_y)

def _handle_new_tab(popup):
    """Handle new tab popup events by getting URL and navigating in main tab instead."""
    try:
        # Wait briefly for the popup to initialize
        time.sleep(0.5)
        # Get the URL of the popup
        popup_url = popup.url
        if (popup_url and popup_url != "about:blank"):
            # Close the popup
            popup.close()
            # Navigate the main page to that URL instead
            page.goto(popup_url)
            print(f"Redirected popup to main tab: {popup_url}")
    except Exception as e:
        print(f"Error handling popup: {e}")
        # Try to close the popup anyway
        try:
            popup.close()
        except:
            pass
