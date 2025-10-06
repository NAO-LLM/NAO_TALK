import os
from dotenv import load_dotenv
from typing import Annotated,Sequence, TypedDict
from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph.message import add_messages # helper function to add messages to the state
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END

from nao import fazer_onda, chutar, elefante, saxofone, tirar_foto, taichi, disco, descansar, levantar, sentar #movimentos padrão

load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    number_of_steps: int

tools = [fazer_onda, chutar, elefante, saxofone, tirar_foto, taichi, disco, descansar, levantar, sentar]
    
# Create LLM class
llm = ChatGoogleGenerativeAI(
    model= "gemini-1.5-flash",
    temperature=1.0,
    max_retries=2,
    google_api_key=gemini_api_key,
)

# Bind tools to the model
model = llm.bind_tools(tools)

tools_by_name = {tool.name: tool for tool in tools}

# Define our tool node
def call_tool(state: AgentState):
    outputs = []
    # Iterate over the tool calls in the last message
    for tool_call in state["messages"][-1].tool_calls:
        # Get the tool by name
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            ToolMessage(
                content=tool_result,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}

def call_model(
    state: AgentState,
    config: RunnableConfig,
):
    # Invoke the model with the system prompt and the messages
    response = model.invoke(state["messages"], config)
    # We return a list, because this will get added to the existing messages state using the add_messages reducer
    return {"messages": [response]}


# Define the conditional edge that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]
    # If the last message is not a tool call, then we finish
    if not messages[-1].tool_calls:
        return "end"
    # default to continue
    return "continue"

# Define a new graph with our state
workflow = StateGraph(AgentState)

# 1. Add our nodes 
workflow.add_node("llm", call_model)
workflow.add_node("tools",  call_tool)
# 2. Set the entrypoint as `agent`, this is the first node called
workflow.set_entry_point("llm")
# 3. Add a conditional edge after the `llm` node is called.
workflow.add_conditional_edges(
    # Edge is used after the `llm` node is called.
    "llm",
    # The function that will determine which node is called next.
    should_continue,
    # Mapping for where to go next, keys are strings from the function return, and the values are other nodes.
    # END is a special node marking that the graph is finish.
    {
        # If `tools`, then we call the tool node.
        "continue": "tools",
        # Otherwise we finish.
        "end": END,
    },
)
# 4. Add a normal edge after `tools` is called, `llm` node is called next.
workflow.add_edge("tools", "llm")

# Now we can compile and visualize our graph
graph = workflow.compile()  

if __name__ == "__main__":
    # Create our initial message dictionary
    inputs = {"messages": [("user", f"NAO, faça uma pose taichi")]}

    # call our graph with streaming to see the steps
    for state in graph.stream(inputs, stream_mode="values"):
        last_message = state["messages"][-1]
        last_message.pretty_print()