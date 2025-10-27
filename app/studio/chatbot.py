import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "text-to-sql-agent"

from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage

from src.agent import ChatAgent
from src.prompt import system_message
from src.tools import run_query

# Initialize tools and agent at module level
tools = [run_query]
sql_llm = ChatOpenAI(model="gpt-3.5-turbo")
summary_llm = ChatOpenAI(model="gpt-3.5-turbo")
SQLAgent = ChatAgent(llm=sql_llm, tools=tools, system_message=system_message)

# State class to store messages and summary
class SQLState(MessagesState):
    summary: str

# Define node functions
def sql_assistant(state: SQLState):
    """Handle SQL assistant responses and tool calls with summary context"""
    # Get summary if it exists
    summary = state.get("summary", "")
    # Create system message with or without summary
    if summary:
        enhanced_system_message = f"{system_message}\n\nSummary of conversation earlier: {summary}"
    else:
        enhanced_system_message = system_message
    
    # Ensure we have proper message flow - don't modify existing messages
    # Just pass the current state and let SQLAgent handle it
    # Add summary context to the agent's system message if needed
    temp_state = {**state}
    
    # Update the agent's system message for this call
    original_system = SQLAgent.system_message
    SQLAgent.system_message = enhanced_system_message
    
    try:
        result = SQLAgent.node(temp_state)
    finally:
        # Restore original system message
        SQLAgent.system_message = original_system
    
    return result


def should_continue(state: SQLState) -> Literal["tools", "summarize_conversation", "__end__"]:
    """Determine next node: tools, summarize, or end"""
    messages = state["messages"]
    
    # Check if last message is a tool call
    last_message = messages[-1] if messages else None
    
    # If tool call, go to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"

    # If there are more than 15 messages, summarize the conversation
    if len(messages) > 15:
        return "summarize_conversation"
    
    # Otherwise end
    return "__end__"

def summarize_conversation(state: SQLState):
    """Summarize the conversation and keep recent messages"""
    # Get existing summary
    summary = state.get("summary", "")
    
    # Create summarization prompt
    if summary:
        summary_message = (
            f"This is summary of the SQL conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above, "
            "focusing on SQL queries, results, and user requirements:"
        )
    else:
        summary_message = (
            "Create a summary of the SQL conversation above, "
            "focusing on SQL queries executed, results obtained, and user requirements:"
        )
    
    # Add prompt to messages for summarization
    messages_for_summary = state["messages"] + [HumanMessage(content=summary_message)]
    response = summary_llm.invoke(messages_for_summary)
    
    # Keep the last 6 messages to preserve tool call/response pairs
    # This is safer than trying to parse tool call chains
    messages_to_keep = 6
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-messages_to_keep]]
    
    return {
        "summary": response.content, 
        "messages": delete_messages
    }

# Define the graph workflow
workflow = StateGraph(SQLState)

# Add nodes
workflow.add_node("sql_assistant", sql_assistant)
workflow.add_node("tools", ToolNode(SQLAgent.tools))
workflow.add_node("summarize_conversation", summarize_conversation)

# Define edges
workflow.add_edge(START, "sql_assistant")
workflow.add_conditional_edges("sql_assistant", should_continue)
workflow.add_edge("tools", "sql_assistant")
workflow.add_edge("summarize_conversation", "sql_assistant")

# Compile with memory
memory = MemorySaver()
graph = workflow.compile()

def run_graph():
    """Run the SQL agent graph with memory management"""
    config = {"configurable": {"thread_id": "1"}}
    messages = [HumanMessage(content="What is the highest price of product SMP in EEX EU in the past 2 years?")]

    result = graph.invoke({"messages": messages}, config, recursion_limit=10)
    
    print("\n=== Final Messages ===")
    for m in result['messages']:
        m.pretty_print()
    
    # Print summary if it exists
    if result.get('summary'):
        print(f"\n=== Conversation Summary ===\n{result['summary']}")

if __name__ == "__main__":
    run_graph()