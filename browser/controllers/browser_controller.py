"""
Main browser controller that serves as the interface to all browser functionality.
"""

import asyncio
from browser.controllers.element_controller import click, fill_input, select_option
from browser.controllers.keyboard_controller import keyboard_action
from browser.analyzers.page_analyzer import analyze_page
from browser.navigation.navigator import navigate, go_back
from browser.navigation.scroll_manager import scroll
from browser.utils.user_interaction import ask_user

# Global page reference
page = None

async def initialize(browser_page):
    # Import locally to avoid circular imports
    from browser.controllers.element_controller import initialize as init_element
    from browser.controllers.keyboard_controller import initialize as init_keyboard
    from browser.analyzers.page_analyzer import initialize as init_analyzer
    from browser.navigation.navigator import initialize as init_navigator
    from browser.navigation.scroll_manager import initialize as init_scroll
    from browser.utils.dom_helpers import initialize as init_dom_helpers
    from browser.utils.user_interaction import initialize as init_user_interaction
    
    global page
    page = browser_page
    
    # Initialize all sub-controllers
    await init_element(page)
    await init_keyboard(page)
    await init_analyzer(page)
    await init_navigator(page)
    await init_scroll(page)
    await init_dom_helpers(page)
    init_user_interaction()
    
    print("Browser controller initialized successfully")

async def close():
    try:
        await page.context.browser.close()
        return "Browser closed successfully"
    except Exception as e:
        return f"Error closing browser: {str(e)}"

def get_browser_tools():
    browser_tools = [
        analyze_page,
        click,
        keyboard_action,
        fill_input,
        select_option,
        go_back,
        navigate,
        scroll,
        ask_user,
    ]
    
    return browser_tools