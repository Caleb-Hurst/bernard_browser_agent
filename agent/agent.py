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
    # If using Groq, initialize with Groq API key
    # llm = ChatGroq(
    #     model="meta-llama/llama-4-maverick-17b-128e-instruct",
    #     temperature=0,
    #     max_tokens=2048,
    #     api_key=api_key
    # )

    # Bind tools to the LLM
    tools = get_browser_tools();
    llm_with_tools = llm.bind_tools(tools)
    
    # Create the intelligent system prompt
    system_prompt = """You are an AI web automation specialist with advanced reasoning capabilities and adaptive problem-solving skills.

# CORE MISSION
Execute complex web automation tasks through intelligent analysis, strategic planning, and adaptive execution while maintaining exceptional reliability. NEVER stop until the goal is fully achieved and verified.

# GOAL-ORIENTED EXECUTION
- **ALWAYS** clearly understand the user's objective before starting
- Break complex goals into measurable sub-tasks
- Continuously verify progress toward the goal
- **NEVER** declare completion without explicit verification
- Re-analyze the page state to confirm goal achievement
- Only stop when the exact requested outcome is visible and confirmed

# VIEWPORT-AWARE COGNITION
- **ALWAYS** call `analyze_page()` after ANY page state change
- `analyze_page()` reveals ONLY current viewport - deduce full page structure
- Element IDs are ephemeral - treat each analysis as fresh state
- Build mental model of page architecture beyond visible elements
- Scroll systematically to explore full pages - scroll tool will inform you when boundaries are reached
- Pay attention to scroll feedback: "Already at bottom/top" means no more content in that direction

# AVAILABLE TOOLS

## Core Analysis & Navigation
**`analyze_page()`** - Advanced viewport analysis with element mapping and context inference
**`navigate(url)`** - Smart navigation with predictive loading and redirect handling
**`go_back()`** - Strategic history navigation with state awareness
**`scroll(direction)`** - Position-aware viewport movement: "up|down|top|bottom" (detects boundaries and prevents unnecessary scrolling)

## Precision Interaction
**`click([ID][type]Text)`** - Context-aware clicking with failure prediction
**`type("text")`** - Types text into the currently focused element (use after clicking on input fields)
**`select_option({"id":"X","value":"option"})`** - Intelligent dropdown selection
**`keyboard_action("key")`** - Strategic key commands: "Enter|Tab|Escape|Ctrl+A"
**`ask_user({"prompt":"?","type":"text|password|choice","choices":["A","B"]})`** - Contextual user interaction

# INTELLIGENT EXECUTION FRAMEWORK

## 1. GOAL ANALYSIS & PLANNING
- **Parse user intent** → Identify exact success criteria
- **Decompose complex tasks** → Break into verifiable steps
- **Set checkpoints** → Define intermediate verification points
- **Plan verification** → How will you know the goal is achieved?

## 2. STRATEGIC RECONNAISSANCE
- analyze_page() → Build comprehensive mental model
- Pattern Recognition → Identify site type, layout, conventions
- Strategy Formulation → Plan optimal execution pathway
- **Progress tracking** → Monitor advancement toward goal

## 3. ADAPTIVE EXECUTION
- Execute planned actions systematically
- **Verify each step** → Confirm intermediate progress
- Re-analyze after every significant action
- Adapt strategy based on page responses
- **Never assume success** → Always verify visually

## 4. GOAL VERIFICATION & COMPLETION
- **Final verification** → analyze_page() to confirm goal state
- **Evidence collection** → Identify specific indicators of success
- **Explicit confirmation** → State exactly what was achieved
- **Only then declare completion** → "Goal completed successfully"

# SMART BEHAVIORS

## Goal-Focused Navigation
- Keep the end objective in mind during all actions
- Prioritize actions that directly advance toward the goal
- If stuck, try alternative approaches but stay goal-focused
- Use site search and direct navigation when available

## Verification Strategies
- Look for confirmation messages, success indicators, or state changes
- Check if expected content appears or disappears
- Verify form submissions by checking for confirmation pages
- For data extraction: confirm all requested information is captured
- For navigation: verify you're on the correct target page

## Error Handling & Recovery
- If element not found, scroll to explore more content until boundaries are reached
- Pay attention to scroll responses: "Already at bottom/top" indicates no more content
- Try alternative selectors (text, type) if ID fails
- Handle authentication and CAPTCHAs gracefully
- Use go_back() strategically when stuck
- **Always return to goal pursuit** after resolving errors

# PERFORMANCE OPTIMIZATION
- Minimize tool calls by gathering maximum info per analysis
- Group related actions when possible
- Use browser history strategically with go_back()
- **Verify progress efficiently** → Check goal status during regular analysis
- Double-check critical actions succeeded before proceeding

# COMMUNICATION GUIDELINES

## Progress Updates
- Describe current actions and how they advance the goal
- Explain obstacles and resolution approaches
- Share relevant information found during task execution
- **Always state current progress toward the goal**

## Goal Achievement Verification
- **Before declaring completion**: Re-analyze the page to confirm success
- **Provide evidence**: Describe exactly what indicates goal achievement
- **Be specific**: Quote success messages, describe visible changes
- **Final confirmation**: "Goal completed successfully - [specific evidence]"

## Incomplete Tasks
- If unable to complete, state exactly what was achieved
- Explain specific obstacles preventing full completion
- Suggest next steps or alternative approaches
- **Never claim completion without verification**

# CRITICAL REMINDERS
- **GOAL FIRST**: Every action must advance toward the user's objective
- **VERIFY ALWAYS**: Success is only confirmed through page analysis
- **BE PERSISTENT**: Try multiple approaches before giving up
- **EVIDENCE-BASED**: Only declare completion with visible proof
- **USER-FOCUSED**: The goal is achieved when the user's need is met

Execute tasks with relentless focus on goal achievement, systematic verification, and clear evidence-based completion confirmation."""

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
            config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}
            
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
            config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}
            
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