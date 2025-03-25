from langchain.tools import Tool

def create_browser_tools(controller):
    """Create LangChain tools for browser automation."""
    
    return [
        Tool(
            name="Navigate",
            func=lambda url: controller.navigate(url.strip("'\"").strip()),
            description="Navigate to a URL with virtual mouse movement to address bar. Input: URL (string)."
        ),
        Tool(
            name="VisualClick",
            func=lambda desc: controller.visual_click(desc.strip("'\"").strip()),
            description=f"Click an element using visual analysis when regular DOM methods fail. Input: JSON object with element id, type and text, e.g. {{\"id\": \"5\", \"type\": \"button\", \"text\": \"add to cart\"}}. This helps target specific elements on the page with higher precision."
        ),
        Tool(
            name="AnalyzePage",
            func=lambda *args: controller.analyze_page(),
            description="Analyze the page's structure and content using DOM traversal. Returns a comprehensive structured report that includes: 1) Page metadata (title, URL), 2) Interactive elements organized by type with IDs and descriptions, and 3) Text content hierarchically organized by headings, paragraphs and other content types. The output is formatted for easy reading and reference. No input needed."
        ),
        Tool(
            name="Type",
            func=lambda text: controller.type_text(text.strip("'\"").strip()),
            description="Type text character by character with realistic human timing. Input: text to type (string)."
        ),
        Tool(
            name="PressEnter",
            func=lambda *args: controller.press_enter(),
            description="Press the Enter key. Important: You must include 'Action Input:' line after 'Action: PressEnter', but leave it empty as this tool does not require any input."
        ),
        Tool(
            name="Scroll",
            func=lambda direction="down": controller.scroll(direction),
            description="Scroll the page with virtual mouse wheel. Input: direction ('up', 'down', 'top', or 'bottom')."
        ),
        Tool(
            name="Type",
            func=lambda text: controller.type_text(text.strip("'\"").strip()),
            description="Type text character by character with realistic human timing. Input: text to type (string)."
        ),
        Tool(
            name="GoogleSearch",
            func=lambda query: controller.search_for(query.strip("'\"").strip()),
            description="Execute a Google search query. Input: search query (string). Use this for searching on Google."
        ),
    ]