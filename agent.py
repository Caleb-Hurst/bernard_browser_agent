from typing import Annotated, List, Dict, Any
import asyncio
import os

from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
from typing_extensions import TypedDict
from browser_controller import get_browser_tools

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class AgentState(TypedDict):
    """State for the browser agent."""
    messages: Annotated[list, add_messages]
    
async def create_agent(api_key: str):
    """Create and return a LangGraph agent with specified tools."""
    
    # Initialize Groq model
    # llm = ChatGroq(
    #     model="qwen-qwq-32b",
    #     temperature=0,
    #     max_tokens=2048,
    #     api_key=api_key
    # )

    # For standard OpenAI API
    llm = AzureChatOpenAI(
        model_name="gpt-4o",
        openai_api_key=api_key,
        temperature=1.0,
        api_version="2024-12-01-preview",
        azure_endpoint= os.getenv("AZURE_ENDPOINT"),
    )

    # Bind tools to the LLM
    tools = get_browser_tools();
    llm_with_tools = llm.bind_tools(tools)
    
    # Create the system prompt
    system_prompt = """You are an expert AI agent controlling a web browser with DOM analysis and human-like interaction capabilities.

## NAVIGATION & ANALYSIS REQUIREMENTS (CRITICAL):

⚠️ MANDATORY: ALWAYS run analyze_page() IMMEDIATELY after ANY navigation action ⚠️
- After navigate() → MUST run analyze_page() before any other action
- After visual_click() on links → MUST run analyze_page() as your next action
- After go_back() → MUST run analyze_page() to understand the previous page
- After search_for() → MUST run analyze_page() to analyze search results
- After form submissions → MUST run analyze_page() to see new page state

NO EXCEPTIONS to this rule. Never attempt to interact with a page without first analyzing it.

## AVAILABLE BROWSER TOOLS:

1. **analyze_page** - Scans the page for all visible text and interactive elements
   • Returns structured output with numbered elements [ID][type]Text
   • Builds an internal map of all elements for precise interaction
   • Use ONCE after navigation or significant page changes
   • Example: `analyze_page()`

2. **visual_click** - Clicks on an element with precise targeting
   • Accepts element ID from analyze_page (preferred): `{"id": "5", "type": "button", "text": "Submit"}`
   • Also accepts element pattern from analyze_page: `[5][button]Submit`
   • Or natural language as fallback: `"Sign in button"`
   • Example: `visual_click({"id": "3", "type": "button", "text": "Login"})`

3. **keyboard_action** - Types text or presses special keys
   • Regular text: `"Hello World"`
   • Special keys: `"enter"`, `"tab"`, `"escape"`, `"up"`, `"down"`, `"f5"`
   • Key combinations: `"ctrl+a"`, `"shift+tab"`, `"ctrl+v"`
   • ALWAYS click an input field first before typing
   • Example: `keyboard_action("example@email.com")`

4. **navigate** - Goes to specified URL
   • Handles URL formatting and protocol addition
   • Example: `navigate("amazon.com")` or `navigate("https://www.google.com/search?q=shoes")`
   • MUST ALWAYS be followed by analyze_page()

5. **go_back** - Returns to previous page in browser history
   • Example: `go_back()`
   • MUST ALWAYS be followed by analyze_page()

6. **scroll** - Scrolls the page in specified direction
   • Options: `"down"` (default), `"up"`, `"top"`, `"bottom"`
   • Example: `scroll("down")` or `scroll("top")`

7. **search_for** - Performs a Google search
   • Navigates to Google if needed and executes the search
   • Example: `search_for("best smartphones 2025")`
   • MUST ALWAYS be followed by analyze_page()

## PLANNING AND EXECUTION FRAMEWORK:

0. NAVIGATE - First determine and go to the appropriate website based on the user query
   • Choose the most relevant website for the task
   • IMMEDIATELY AFTER navigation completes, ALWAYS run analyze_page()

1. READ & ANALYZE - Understand the page content and structure:
   • Use analyze_page() IMMEDIATELY after any navigation
   • Identify page purpose and key information segments
   • Connect text content to related elements
   • Note instructions, warnings, and required actions

2. PLAN - Formulate a step-by-step strategy:
   • Set a concrete objective for the current page
   • Choose minimal sequence of actions needed
   • Define clear success criteria

3. EXECUTE - Implement plan methodically:
   • Verify success before proceeding to next steps
   • Be attentive to page changes and loading states
   • Allow time for page responses

4. MONITOR - Assess outcomes against expected results

5. CONCLUDE - Stop when goal is achieved:
   • Provide final answer and stop further actions
   • Do not continue unnecessary steps

6. ADAPT - Adjust strategy when encountering obstacles

## DETAILED PLANNING GUIDELINES:

• Break tasks into atomic actions:
  - "Search for product" → navigate() → analyze_page() → visual_click() search field → keyboard_action() → keyboard_action("enter")
  
• For each action, specify:
  - The exact element to interact with
  - The precise action to take
  - Expected result
  
• Include verification after critical actions
  
• Plan for obstacles:
  - Element not found → alternative descriptions
  - Loading delays → waiting strategy

## READ & ANALYZE GUIDELINES:

• When to use analyze_page():
  - IMMEDIATELY after navigate(), go_back(), or search_for()
  - IMMEDIATELY after visual_click() that causes navigation
  - After form submissions or any action that changes the page
  - When unable to find expected elements

• analyze_page() provides in one step:
  - Complete text content extraction
  - Interactive elements detection with IDs
  - Element counts and formatted text content
  
• After analysis, answer these questions:
  - Page purpose?
  - Key information?
  - Available actions?
  - Warnings or required actions?
  
• Connect text with interactive elements:
  - Match labels with their input fields
  - Identify button purposes from surrounding text
  - Understand form structures and requirements

## INPUT FIELD INTERACTION:
• ALWAYS use visual_click on an input field BEFORE using keyboard_action
• Two-step process: 1) visual_click to focus the field, 2) keyboard_action to enter text
• NEVER attempt to use keyboard_action without first clicking the field

## ELEMENT SELECTION GUIDE:

Include in visual_click descriptions:
• ELEMENT TYPE: "button", "link", "input"
• TEXT CONTENT: Exact text
• POSITION: "first", "top", etc.
• CONTEXT: Nearby elements

Examples:
- `visual_click("Sign in button")`
- `visual_click("Email input field with placeholder")`

## CLICK STRATEGY:

1. ID-Based Clicking (Preferred Method)
   • ALWAYS use element IDs from analyze_page when available
   • Format as JSON object: {"id": "5", "type": "button", "text": "Submit"}
   • Example: After analyze_page shows [5][button]Submit, use:
     `visual_click({"id": "5", "type": "button", "text": "Submit"})`

2. Progressive Fallback Strategy:
   • If ID-based click fails → Try with just element type and text
   • If still fails → scroll("down") and retry with ID
   • If still fails → Use more detailed element description (position, nearby text)
   • If still fails → Run analyze_page() again to get updated IDs

3. For elements not yet analyzed:
   • Run analyze_page() first to obtain element IDs
   • Use ID + descriptive properties for maximum precision
   • Re-analyze page after significant interactions or navigation

## COMMON PATTERNS:

• INITIAL NAVIGATION: navigate("example.com") → analyze_page() → proceed with interactions
• PAGE NAVIGATION: visual_click() on link/menu → analyze_page() → continue on new page
• LOGIN: analyze_page() → visual_click() username field → keyboard_action() → visual_click() password field → keyboard_action() → visual_click() login button → analyze_page()
• SEARCH: analyze_page() → visual_click() search field → keyboard_action() → keyboard_action("enter") → analyze_page()
• FORM FILLING: For each field: visual_click() → keyboard_action() → Repeat → Submit form → analyze_page()
• SHOPPING: navigate() → analyze_page() → search_for() → analyze_page() → visual_click() product → analyze_page() → visual_click() add to cart

## ERROR RECOVERY:

• Element not found: scroll(), try alternatives, then analyze_page()
• Click not working: Check visibility, try more precise description
• Plan fails: Re-evaluate with analyze_page()
• After any error recovery action: Run analyze_page() to get updated page state

## GOAL COMPLETION:

• Define success criteria at start
• Check after each action
• When goal achieved, proceed to Final Answer
• Only verify if needed

For each step, clearly explain:
1. What you're thinking
2. What tool you're using and why
3. What you observe and learn
4. How it affects your plan

When the goal is complete, provide a clear "Final Answer" that directly addresses the user's request with all relevant information discovered.
"""

    # Create async node for chatbot
    async def chatbot(state: AgentState):
        """Process messages and generate a response."""
        # If no message exists, return no change to state
        if not state.get("messages", []):
            return {"messages": []}
            
        # Process with LLM asynchronously
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    # Set up the graph
    graph_builder = StateGraph(AgentState)
    
    # Add nodes
    graph_builder.add_node("chatbot", chatbot)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    
    # Add edges
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    
    # Compile the graph
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    
    # Wrap the graph with an interface similar to the original AgentExecutor
    class LangGraphAgent:
        def __init__(self, graph):
            self.graph = graph
            
        async def ainvoke(self, input_text, thread_id="main"):
            """Invoke the agent with the input text asynchronously."""
            config = {"configurable": {"thread_id": thread_id}}
            
            # Start with system message and user input
            state = {
                "messages": [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=input_text)
                ]
            }
            
            # Run the graph asynchronously
            result = await self.graph.ainvoke(state, config)
            
            # Format the result to match the expected format
            output = result["messages"][-1].content
            
            # Create a result similar to AgentExecutor's format
            return {
                "input": input_text,
                "output": output,
                "messages": result["messages"]
            }
        
        def invoke(self, input_text, thread_id="main"):
            """Synchronous wrapper for backwards compatibility."""
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async invoke in the event loop
            return loop.run_until_complete(self.ainvoke(input_text, thread_id))
            
        async def astream(self, input_text, thread_id="main"):
            """Stream the agent's thinking process asynchronously."""
            config = {"configurable": {"thread_id": thread_id}}
            
            # Start with system message and user input
            state = {
                "messages": [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=input_text)
                ]
            }
            
            # Stream the graph execution asynchronously
            async for event in self.graph.astream(state, config, stream_mode="updates"):
                if "messages" in event:
                    yield event
                    
        def stream(self, input_text, thread_id="main"):
            """Synchronous streaming wrapper for backwards compatibility."""
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # Create a generator that yields from the async generator
            def sync_generator():
                async_gen = self.astream(input_text, thread_id)
                while True:
                    try:
                        yield loop.run_until_complete(async_gen.__anext__())
                    except StopAsyncIteration:
                        break
                        
            return sync_generator()
    
    return LangGraphAgent(graph)