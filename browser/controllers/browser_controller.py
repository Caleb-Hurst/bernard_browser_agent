"""
Main browser controller that serves as the interface to all browser functionality.
"""

import time
from browser.controllers.element_controller import click, type, select_option
from browser.controllers.keyboard_controller import keyboard_action
from browser.analyzers.page_analyzer import analyze_page
from browser.navigation.navigator import navigate, go_back
from browser.navigation.scroll_manager import scroll
from browser.utils.user_interaction import ask_user

# Global page reference
page = None

def initialize(browser_page):
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
    init_element(page)
    init_keyboard(page)
    init_analyzer(page)
    init_navigator(page)
    init_scroll(page)
    init_dom_helpers(page)
    init_user_interaction()
    
    print("Browser controller initialized successfully")

def close():
    try:
        page.context.browser.close()
        return "Browser closed successfully"
    except Exception as e:
        return f"Error closing browser: {str(e)}"

def get_browser_tools():
    return [
        analyze_page,
        click,
        type,
        select_option,
        keyboard_action,
        navigate,
        go_back,
        scroll,
        ask_user
    ]