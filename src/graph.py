import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "text-to-sql-agent"


from langchain_openai import ChatOpenAI
from IPython.display import Image, display

from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent import ChatAgent
from src.prompt import system_message
from src.tools import run_query
    

def build_graph():
    tools = [run_query]
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    SQLAgent = ChatAgent(llm=llm, tools=tools, system_message=system_message)
    
    # Graph
    builder = StateGraph(MessagesState)

    # Define nodes: these do the work
    builder.add_node("assistant", SQLAgent.node)
    builder.add_node("tools", ToolNode(SQLAgent.tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "assistant")
    builder.add_edge("assistant", END)  # None represents the END node
    
    memory = MemorySaver()
    compiled_graph = builder.compile(checkpointer=memory) 
    return compiled_graph

def run_graph():
    compiled_graph = build_graph()
    # Specify a thread
    config = {"configurable": {"thread_id": "1"},
              "checkpointer": {"thread_id": "1"},
              "recursion_limit": 10
              }

    # Specify an input
    messages = [HumanMessage(content="What is the volatility of product SMP in EEX EU in the last 2 years?")] 
    
    messages = compiled_graph.invoke({"messages": messages},config)
    for m in messages['messages']:
        m.pretty_print()


if __name__ == "__main__":
    run_graph()