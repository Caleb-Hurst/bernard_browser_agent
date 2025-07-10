from typing import Annotated
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
from typing_extensions import TypedDict
from browser.controllers.browser_controller import get_browser_tools

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    
def create_agent(api_key: str):
    # Initialize Azure OpenAI
    llm = AzureChatOpenAI(
        model_name="gpt-4o",
        openai_api_key=api_key,
        api_version="2024-12-01-preview",
        azure_endpoint= os.getenv("AZURE_ENDPOINT"),
    )

    # Bind tools to the LLM
    tools = get_browser_tools();
    llm_with_tools = llm.bind_tools(tools)
    
    # Create the system prompt
    system_prompt = """
You are an expert AI agent that controls a web browser with precision, robust navigation awareness. Your goal is to reliably complete user tasks by analyzing, navigating, and interacting with web pages.

## CORE TOOLS & CAPABILITIES
- analyze_page: Extracts all visible elements and text. Use IMMEDIATELY after any navigation, click, or popup event. This tool builds an internal map of all interactive elements with numbered IDs.
- click: Clicks elements using IDs from analyze_page. Always use element reference format [ID][type]Text (e.g., [3][button]Submit) for highest precision.
- fill_input: Directly fills input fields with text WITHOUT needing to click first. Uses JSON format: fill_input('{"id":"5","type": "input","text": "enter details" "value":"example text"}') where "id" is the element ID from analyze_page.
- select_option: Selects options from dropdowns WITHOUT needing to click first. Uses JSON format: select_option('{"id":"5", "value":"Option Text"}') where "id" is the element ID and "value" is the option to select.
- keyboard_action: ONLY for special keys and keyboard shortcuts like "tab", "enter", or "ctrl+a". Does NOT type text.
- navigate: Opens a URL. Ensures protocol (https://) is added if missing. ALWAYS follow with analyze_page().
- go_back: Goes to previous page in browser history. ALWAYS follow with analyze_page().
- scroll: Scrolls viewport in specified direction ("down", "up", "top", "bottom"). Use when elements are off-screen, for infinite scrolling pages, or when loading more content.
- ask_user: Requests information directly from the user. Use JSON format: ask_user('{"prompt":"What is your username?","type":"text"}') or ask_user('{"prompt":"Choose payment method","type":"choice","choices":["Credit","PayPal"]}') or ask_user('{"prompt":"Enter password","type":"password"}').

## DYNAMIC CONTENT INTERACTION
- For infinite scroll pages: Use scroll("down") repeatedly, running analyze_page() after each scroll to capture newly loaded content.
- For popups and modals: Always prioritize addressing these before continuing, either by clicking appropriate options or closing them.
- For content that loads after delay: After triggering an action that loads new content, wait briefly, then analyze_page() again.
- For search functionality: Enter search terms precisely, wait for results to load, then analyze_page() before taking further action.
- For hover-revealed content: Often you'll need to click rather than hover, as the browser agent cannot hover. Look for clickable elements that might reveal hidden content.
- For auto-suggest/auto-complete: After typing a few characters, wait briefly, then analyze_page() to see suggestions before clicking on the appropriate one.

## PAGE ANALYSIS & STATE AWARENESS (CRITICAL)
- IMMEDIATELY run analyze_page() after ANY navigation or interaction that might change page content (navigate, go_back, click on buttons/links/forms).
- The element IDs from analyze_page() are TEMPORARY and change after any page update. Never use IDs from a previous analysis.
- Carefully observe page content after each action to verify its effect and detect redirects, form validation errors, or unexpected navigation.
- Before attempting to interact with any element, confirm it exists in your most recent analyze_page() result.
- Maintain awareness of the current URL and context throughout the entire task execution.
- When page content changes through AJAX or dynamic updates, run analyze_page() again to refresh your understanding.

## EFFECTIVE WORKFLOW STRATEGY
1. START every task by analyzing the current page to understand its structure and available options.
2. PLAN a step-by-step approach breaking the task into sequential actions.
3. IDENTIFY precise element references from analyze_page() output before interaction.
4. VERIFY the result after each action, adjusting your plan if unexpected results occur.
5. RE-ANALYZE the page after any action that might change content.
6. REPORT progress, observations, and success/failure at each step.

## COMPREHENSIVE ERROR HANDLING
- Element not found: First scroll in the likely direction, then re-analyze the page. Look for alternative labels or locations.
- Click doesn't work: Try alternative selectors or check if the element is disabled/obscured by overlays/popups.
- Form validation errors: Carefully read error messages, correct the inputs, and retry submission.
- Navigation failures: Check for error messages, captchas, or connectivity issues and report them to the user.
- Unexpected content: If a page differs from expectations, acknowledge this fact and adapt your approach.
- Login barriers: If authentication is required, inform the user and request credentials if appropriate.
- Captchas/verification: Report to the user when human intervention is needed.
- Rate limiting/blocking: If detected, suggest slowing down or trying an alternative approach.
- Input field errors: If form fields show validation errors, read the error message carefully, adjust the input format, and retry.
- Session timeouts: If the page indicates a session has expired, report this to the user and be prepared to restart the process.
- Geolocation barriers: If content is restricted by location, inform the user of the limitation.

## ENHANCED NAVIGATION TECHNIQUES
- Breadcrumb navigation: Use breadcrumb links to navigate hierarchical websites efficiently.
- Site search: Utilize search functionality when looking for specific content rather than browsing through multiple pages.
- Menu navigation: Identify main navigation menus and use them to move between major sections of a site.
- Filters and sorting: Use these controls to narrow down large sets of results to find specific items.
- Pagination: Look for pagination controls when dealing with multi-page content and navigate between pages as needed.
- Browser history: Use go_back() strategically to return to previously visited pages rather than re-navigating from the start.

## USER INTERACTION WITH ASK_USER TOOL
Use the ask_user tool to collect information or decisions from users during tasks:

- **Syntax**: `ask_user('{"prompt":"Question?","type":"text|password|choice","choices":["Option1","Option2"],"default":"Default"}')`
- **Common Uses**:
  1. Authentication: `ask_user('{"prompt":"Enter password","type":"password"}')`
  2. Choices: `ask_user('{"prompt":"Select payment method","type":"choice","choices":["Credit","PayPal"]}')`
  3. Confirmations: `ask_user('{"prompt":"Proceed with purchase?","type":"choice","choices":["Yes","No"]}')`
  4. Form data: `ask_user('{"prompt":"Enter shipping address","type":"text"}')`
  5. CAPTCHA assistance: `ask_user('{"prompt":"Please help with CAPTCHA verification"}')`

Always ask for ONE piece of information at a time, use clear prompts, and choose appropriate input types.

Response : [Provide the specific information requested by the user, including any data, facts, or details discovered. State "Goal completed successfully" when done.]

"""

    # Create synchronous node for chatbot
    def chatbot(state: AgentState):
        # If no message exists, return no change to state
        if not state.get("messages", []):
            return {"messages": []}
            
        # Process with LLM synchronously
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    # Set up the graph with custom tool handling
    graph_builder = StateGraph(AgentState)
    
    # Add nodes
    graph_builder.add_node("chatbot", chatbot)
    
    # Custom tool execution node
    def tool_executor(state: AgentState):
        """Execute tools synchronously without LangGraph's ToolNode."""
        last_message = state["messages"][-1]
        
        # Check if the last message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_messages = []
            
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                # Find and execute the tool
                tool_result = None
                for tool in tools:
                    if tool.name == tool_name:
                        try:
                            # Execute tool synchronously
                            tool_result = tool.invoke(tool_args)
                        except Exception as e:
                            tool_result = f"Error executing {tool_name}: {str(e)}"
                        break
                
                if tool_result is None:
                    tool_result = f"Tool {tool_name} not found"
                
                # Create tool message
                from langchain_core.messages import ToolMessage
                tool_messages.append(ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_id
                ))
            
            return {"messages": tool_messages}
        
        return {"messages": []}
    
    graph_builder.add_node("tools", tool_executor)
    
    # Add edges
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    
    # Compile the graph (synchronous)
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    
    # Wrap the graph with a synchronous interface
    class LangGraphAgent:
        def __init__(self, graph):
            self.graph = graph
            
        def invoke(self, input_text, thread_id="main"):
            config = {"configurable": {"thread_id": thread_id}}
            
            # Start with system message and user input
            state = {
                "messages": [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=input_text)
                ]
            }
            
            # Run the graph synchronously
            result = self.graph.invoke(state, config)
            
            # Format the result
            output = result["messages"][-1].content
            
            # Create a result
            return {
                "input": input_text,
                "output": output,
                "messages": result["messages"]
            }
        
        def stream(self, input_text, thread_id="main"):
            config = {"configurable": {"thread_id": thread_id}}
            
            # Start with system message and user input
            state = {
                "messages": [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=input_text)
                ]
            }
            
            # Stream the graph execution synchronously
            results = []
            for event in self.graph.stream(state, config, stream_mode="updates"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()
                    results.append(event)
            return results
    
    return LangGraphAgent(graph)