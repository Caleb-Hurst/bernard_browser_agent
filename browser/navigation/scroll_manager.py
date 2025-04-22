"""
Scroll manager for browser page scrolling and position management.
"""

import asyncio
import random
from langchain_core.tools import tool

# Global variable to store the page
page = None

async def initialize(browser_page):
    """Initialize the scroll manager."""
    global page
    page = browser_page

@tool
async def scroll(direction="down"):
    """
    Scrolls the page in the specified direction.
    
    Parameters:
        direction: Where to scroll
            - "down" (default): Scrolls down a moderate amount
            - "up": Scrolls up a moderate amount
            - "top": Jumps to the top of the page
            - "bottom": Jumps to the bottom of the page
    
    Returns: Status message indicating scroll result
    """
    try:
        # Clean input and handle quoted strings
        if isinstance(direction, str):
            direction = direction.lower().strip("'\"").strip()
        
        # Get viewport size with fallback
        viewport = page.viewport_size
        
        # Check if viewport is valid before accessing its properties
        if (viewport is None):
            # Fallback to direct JavaScript scrolling when viewport size can't be determined
            if (direction == "down"):
                await page.evaluate("window.scrollBy(0, 300)")
                return "Scrolled down (fallback method)"
            elif (direction == "up"):
                await page.evaluate("window.scrollBy(0, -300)")
                return "Scrolled up (fallback method)"
            elif (direction == "top"):
                await page.evaluate("window.scrollTo(0, 0)")
                return "Scrolled to top"
            elif (direction == "bottom"):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                return "Scrolled to bottom"
            else:
                await page.evaluate("window.scrollBy(0, 300)")
                return f"Invalid direction '{direction}', defaulted to scrolling down"
        
        # If viewport is valid, use normal mouse wheel movement
        center_x = viewport["width"] / 2
        center_y = viewport["height"] / 2
        
        # Get element controller's mouse movement function
        from browser.controllers.element_controller import _natural_mouse_move
        await _natural_mouse_move(center_x, center_y)
        await asyncio.sleep(0.3)
        
        # Determine scroll amount and direction
        if (direction == "down"):
            # Scroll gradually
            for _ in range(3):
                await page.mouse.wheel(0, 100)
                await asyncio.sleep(random.uniform(0.2, 0.4))
            return "Scrolled down"
        elif (direction == "up"):
            # Scroll gradually
            for _ in range(3):
                await page.mouse.wheel(0, -100)
                await asyncio.sleep(random.uniform(0.2, 0.4))
            return "Scrolled up"
        elif (direction == "top"):
            # Go to top
            await page.evaluate("window.scrollTo(0, 0)")
            return "Scrolled to top"
        elif (direction == "bottom"):
            # Go to bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            return "Scrolled to bottom"
        else:
            # Default to scrolling down if invalid input
            for _ in range(3):
                await page.mouse.wheel(0, 100)
                await asyncio.sleep(random.uniform(0.2, 0.4))
            return f"Invalid direction '{direction}', defaulted to scrolling down"
    except Exception as e:
        # Add more detailed error information for debugging
        print(f"Scroll error details: {e}")
        
        # Last resort fallback if any part of the scroll handling fails
        try:
            # Try the simplest possible scrolling method
            await page.evaluate(f"""
                () => {{
                    if ('{direction}' === 'top') window.scrollTo(0, 0);
                    else if ('{direction}' === 'bottom') window.scrollTo(0, document.body.scrollHeight);
                    else if ('{direction}' === 'up') window.scrollBy(0, -300);
                    else window.scrollBy(0, 300);
                }}
            """)
            return f"Emergency scroll fallback used for direction: {direction}"
        except Exception as fallback_error:
            return f"Error scrolling: {str(e)} - Fallback also failed: {str(fallback_error)}"
