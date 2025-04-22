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

async def click(page, x, y):
    """
    Perform a realistic mouse click at specified coordinates.
    
    This function simulates a human-like click by:
    1. Moving the mouse to the target location
    2. Pressing the mouse button down
    3. Waiting a realistic amount of time
    4. Releasing the mouse button
    
    Args:
        page: The browser page object
        x: The x coordinate to click
        y: The y coordinate to click
    """
    try:
        # Update cursor position
        await update_cursor(page, x, y)
        
        # Small delay before clicking (as if positioning)
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Press mouse down
        await page.mouse.move(x, y)
        await page.mouse.down()
        
        # Realistic hold time
        await asyncio.sleep(random.uniform(0.08, 0.15))
        
        # Release mouse
        await page.mouse.up()
        
        # Small delay after clicking
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        print(f"Clicked at position ({x}, {y})")
    except Exception as e:
        print(f"Error performing click: {e}")