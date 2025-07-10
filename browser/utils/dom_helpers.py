"""
DOM helper utilities for working with browser elements.
"""

import re
import time

# Global variable to store the page
page = None

def initialize(browser_page):
    """Initialize the DOM helpers module."""
    global page
    page = browser_page

def _parse_click_target(target_description):
    """Parse target description into ID, type and text components."""
    target_id = None
    target_type = None
    target_text = None
    is_structured = False
    
    # Try to parse structured input (dict or JSON format)
    if isinstance(target_description, dict):
        # Handle case where input is already a dictionary
        target_id = target_description.get('id')
        target_type = target_description.get('type', '').lower() if target_description.get('type') else None
        target_text = target_description.get('text', '').lower() if target_description.get('text') else None
        if target_id or target_type or target_text:
            is_structured = True
            print(f"Using dictionary input: id='{target_id}', type='{target_type}', text='{target_text}'")
    # Handle JSON string input
    elif isinstance(target_description, str) and target_description.startswith('{') and target_description.endswith('}'):
        try:
            # First try to parse as JSON
            import json
            try:
                parsed_input = json.loads(target_description)
                if isinstance(parsed_input, dict):
                    target_id = parsed_input.get('id')
                    target_type = parsed_input.get('type', '').lower() if parsed_input.get('type') else None
                    target_text = parsed_input.get('text', '').lower() if parsed_input.get('text') else None
                    if target_id or target_type or target_text:
                        is_structured = True
                        print(f"Using JSON structured input: id='{target_id}', type='{target_type}', text='{target_text}'")
            except json.JSONDecodeError:
                # If not valid JSON, fall back to simple parsing
                content = target_description.strip('{}').strip()
                parts = [part.strip() for part in content.split(',')]
                
                for part in parts:
                    if ':' in part:
                        key, value = [item.strip() for item in part.split(':', 1)]
                        if key.lower() == 'id':
                            target_id = value
                        elif key.lower() == 'type':
                            target_type = value.lower()
                        elif key.lower() == 'text':
                            target_text = value.lower()
                
                if target_id or target_type or target_text:
                    is_structured = True
                    print(f"Using structured input: id='{target_id}', type='{target_type}', text='{target_text}'")
        except Exception as e:
            print(f"Error parsing input: {e}, using as free text instead")
    
    # Handle direct ID pattern extraction (like [3][button]Submit)
    if not is_structured and isinstance(target_description, str):
        id_type_pattern = re.match(r'\[(\d+)\]\[(.*?)\](.*)', target_description)
        if id_type_pattern:
            target_id = id_type_pattern.group(1)
            target_type = id_type_pattern.group(2).lower()
            target_text = id_type_pattern.group(3)
            is_structured = True
            print(f"Extracted from pattern: id='{target_id}', type='{target_type}', text='{target_text}'")
    
    return target_id, target_type, target_text, is_structured


def _scroll_element_into_view(element):
    """
    Scroll an element into view using DOM methods.
    
    Args:
        element (dict): Element information with at least center_x, center_y
    """
    try:
        # Use scrollIntoView via JS for more reliable scrolling
        page.evaluate("""
            (coords) => {
                const element = document.elementFromPoint(
                    coords.x - window.pageXOffset, 
                    coords.y - window.pageYOffset
                );
                
                if (element) {
                    // Use smooth scrolling with centering
                    element.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center',
                        inline: 'center'
                    });
                    return true;
                } else {
                    // Fallback to coordinate-based scrolling
                    window.scrollTo({
                        top: coords.y - (window.innerHeight / 2),
                        left: coords.x - (window.innerWidth / 2),
                        behavior: 'smooth'
                    });
                    return false;
                }
            }
        """, {
            'x': element['center_x'],
            'y': element['center_y']
        })
    except Exception as e:
        print(f"Error scrolling element into view: {e}")
        # Fallback to regular scrolling
        page.evaluate(f"""
            () => window.scrollTo({{
                top: {element['center_y']} - (window.innerHeight / 2),
                behavior: 'smooth'
            }})
        """)