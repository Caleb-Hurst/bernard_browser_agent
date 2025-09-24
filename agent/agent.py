from typing import Annotated
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict
from browser.controllers.browser_controller import get_browser_tools
from configurations.config import LLM_PROVIDER, CURRENT_LLM_CONFIG

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def create_agent():
    """Create an agent using the configured LLM provider."""
    config = CURRENT_LLM_CONFIG

    # Initialize LLM based on selected provider
    if LLM_PROVIDER == "openai":
        llm = ChatOpenAI(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=config["api_key"],
            base_url=config.get("base_url")
        )
    elif LLM_PROVIDER == "azure":
        llm = AzureChatOpenAI(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            openai_api_key=config["api_key"],
            azure_endpoint=config["azure_endpoint"],
            api_version=config["api_version"]
        )
    elif LLM_PROVIDER == "groq":
        llm = ChatGroq(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=config["api_key"]
        )
    elif LLM_PROVIDER == "anthropic":
        llm = ChatAnthropic(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=config["api_key"]
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

    print(f"Initialized {LLM_PROVIDER} LLM with model: {config['model']}")

    # Bind tools to the LLM
    tools = get_browser_tools();
    llm_with_tools = llm.bind_tools(tools)

    # Create the intelligent system prompt
    system_prompt = """You are browser controller. Execute complex web automation tasks with intelligent analysis and adaptive execution. NEVER stop until the goal is fully achieved and verified.
CORE PRINCIPLES
- Goal-first: identify success criteria before acting
- Analyze before and after actions: use analyze_page() to understand the current viewport and to verify changes
- Click before type: always focus inputs before typing
- Be systematic: scroll to explore, re-analyze when state changes
- Evidence-based completion: only finish after confirming success on the page

AVAILABLE TOOLS (use via tool calls; do not invent tools)
- analyze_page(): Inspect current viewport (ids, types, text, positions). Use after navigation, clicks, typing, scrolling, or any state change.
- navigate(url)
- go_back()
- scroll(direction): "down" | "up" | "top" | "bottom" (watch for "Already at bottom/top")
- click(target): By element id object, natural language, or direct reference
- type(text): Only after focusing an input with click()
- select_option(json): {"id": "...", "type": "dropdown", "text": "Label", "value": "Option"}
- keyboard_action(key): "Enter" | "Tab" | "Escape" | "Ctrl+A"
- ask_user(json): {"prompt": "Question?", "type": "text/password/choice", "choices": [...], "default": "..."} — request a single value when required

EXECUTION LOOP
1) Analyze goal → define explicit success criteria and plan minimal steps
2) Recon → analyze_page()
3) Act → choose the next tool (common patterns: click → type → keyboard_action("Enter"))
4) Verify → analyze_page() to confirm intended effect
5) Explore as needed → scroll('down') progressively; stop when boundaries are reached
6) Recovery → if an action fails, re-analyze and try an alternate locator/strategy
7) Missing info → use ask_user() with a clear, single-value prompt
8) Repeat until success is verified or you determine it’s impossible with reasons

TARGETING & FORMS
- Prefer stable element references (id/type/text). If click fails, re-analyze and try alternative targets.
- For forms: click input → type value → submit (button click or keyboard_action("Enter")). Use Tab to move between fields. Use select_option for dropdowns.


SUCCESS VERIFICATION
- After meaningful actions, analyze_page() and quote concrete on-page evidence (e.g., confirmation text, page title, success banners)
- Final message must include: "Goal completed successfully — Evidence: <quote>"

COMMUNICATION
- Keep reasoning concise and actionable
- Describe each tool use briefly and why
- If blocked (login walls, captcha, paywall) or impossible, explain clearly and ask_user() for needed info when appropriate
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
