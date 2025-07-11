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