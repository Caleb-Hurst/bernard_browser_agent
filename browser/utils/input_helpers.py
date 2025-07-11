"""
Input helpers for browser interactions that simulate realistic human input.

This module provides utility functions for simulating human-like:
- Mouse movements with natural acceleration and path
- Cursor visualization on the page
- Click interactions with appropriate timing
"""

import time
import random
import math

def update_cursor(page, x, y):
    """
    Update the visual cursor position on the page.
    
    Args:
        page: The browser page object
        x: The x coordinate to move to
        y: The y coordinate to move to
    """
    try:
        # Call the updateAICursor function in the page context
        page.evaluate(f"window.updateAICursor({x}, {y})")
    except Exception as e:
        print(f"Error updating cursor: {e}")

def click(page, current_x, current_y):
    """Click with the virtual cursor."""
    # Change cursor appearance to indicate clicking
    page.evaluate("""
        () => {
            const cursor = document.getElementById('ai-agent-cursor');
            if (cursor) {
                cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.5)';
                setTimeout(() => {
                    cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
                }, 200);
            }
        }
    """)

    # Execute DOM click via JavaScript with special handling for input fields
    click_result = page.evaluate("""
        ({x, y}) => {
            // Calculate viewport-relative coordinates
            const viewX = x - window.pageXOffset;
            const viewY = y - window.pageYOffset;
            
            // Find the element at those coordinates
            const element = document.elementFromPoint(viewX, viewY);
            
            if (!element) {
                console.log('No element found at coordinates', viewX, viewY);
                return {success: false, reason: 'No element found'};
            }
            
            console.log('Found element to click:', element.tagName, element.id, element.className);
            
            // Special handling for input fields to ensure focus
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA' || element.tagName === 'SELECT') {
                // Focus + click sequence for input fields
                try {
                    // Try multiple approaches for maximum compatibility
                    element.focus();
                    element.click();
                    
                    // Force focus with mousedown/mouseup events
                    const mouseDown = new MouseEvent('mousedown', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    element.dispatchEvent(mouseDown);
                    
                    const mouseUp = new MouseEvent('mouseup', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    element.dispatchEvent(mouseUp);
                    
                    // Force selection of input text if present
                    if (element.value) {
                        element.select();
                    }
                    
                    // Ensure element is focused
                    if (document.activeElement !== element) {
                        element.focus();
                    }
                    
                    return {
                        success: true,
                        tagName: element.tagName,
                        id: element.id || '(no id)',
                        className: element.className || '(no class)',
                        inputFocused: true
                    };
                } catch (e) {
                    console.error('Input focus error:', e);
                }
            }
            
            // Standard click for non-input elements
            element.click();
            
            return {
                success: true,
                tagName: element.tagName,
                id: element.id || '(no id)',
                className: element.className || '(no class)'
            };
        }
    """, {"x": current_x, "y": current_y})
    
    print(f"DOM click result: {click_result}")