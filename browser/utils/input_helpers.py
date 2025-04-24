"""
Input helpers for browser interactions that simulate realistic human input.

This module provides utility functions for simulating human-like:
- Mouse movements with natural acceleration and path
- Cursor visualization on the page
- Click interactions with appropriate timing
"""

import asyncio
import random
import math

async def natural_mouse_move(page, start_x, start_y, end_x, end_y, steps=25):
    """
    Generate a path for natural mouse movement from start to end coordinates.
    
    This function simulates human-like mouse movement by:
    1. Creating a bezier curve with control points between start and end
    2. Adding slight randomness to the path
    3. Varying speed based on distance from control points
    
    Args:
        page: The browser page object
        start_x: Starting x coordinate
        start_y: Starting y coordinate
        end_x: Ending x coordinate
        end_y: Ending y coordinate
        steps: Number of steps in the movement path (default: 25)
    
    Returns:
        list: List of (x, y) coordinate tuples representing the movement path
    """
    # Calculate distance between points
    distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
    
    # Adjust number of steps based on distance
    adjusted_steps = max(10, min(40, int(distance / 20)))
    steps = adjusted_steps
    
    # Generate control points for a bezier curve
    # Control points create a slight curve in the movement
    ctrl_x = (start_x + end_x) / 2 + random.uniform(-distance/5, distance/5)
    ctrl_y = (start_y + end_y) / 2 + random.uniform(-distance/5, distance/5)
    
    # Generate path points using a quadratic bezier curve
    path_points = []
    
    for i in range(steps + 1):
        t = i / steps
        
        # Quadratic bezier formula
        x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * end_x
        y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * end_y
        
        # Add small random variations to simulate human imperfection
        # More variation in the middle of the path, less at start/end
        if 0.1 < t < 0.9:
            jitter = min(10, distance / 50)
            x += random.uniform(-jitter, jitter)
            y += random.uniform(-jitter, jitter)
        
        path_points.append((round(x), round(y)))
    
    return path_points

async def update_cursor(page, x, y):
    """
    Update the visual cursor position on the page.
    
    Args:
        page: The browser page object
        x: The x coordinate to move to
        y: The y coordinate to move to
    """
    try:
        # Call the updateAICursor function in the page context
        await page.evaluate(f"window.updateAICursor({x}, {y})")
    except Exception as e:
        print(f"Error updating cursor: {e}")

async def click(page, current_x, current_y):
    """Click with the virtual cursor."""
    # Change cursor appearance to indicate clicking
    await page.evaluate("""
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
    click_result = await page.evaluate("""
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