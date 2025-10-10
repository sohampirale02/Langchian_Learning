import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated,Sequence
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage,HumanMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from prompts import system_prompt_query_enhancer
from states import AgentState
load_dotenv()


#
from query_enhancer import query_enhancer_node, query_enhancer_tool_node
from deciders import query_enhancer_decider


print(system_prompt_query_enhancer)


#nodes
graph = StateGraph(AgentState)
graph.add_node("query_enhancer_node",query_enhancer_node)
graph.add_node("query_enhancer_tool_node",query_enhancer_tool_node)


#edges
graph.add_edge(START,"query_enhancer_node")
graph.add_edge("query_enhancer_node",END)
graph.add_edge("query_enhancer_tool_node","query_enhancer_node")


#conditional edges
graph.add_conditional_edges(
  "query_enhancer_node",
  query_enhancer_decider,
  {
    "continue":END ,#TODO change this with next node
    "tool_node_edge":"query_enhancer_tool_node"
  }
)


app = graph.compile()

user_query="Create clone of amazon"

initial_state=AgentState(name="",plan=[],user_query=user_query,enhanced_query="",messages=[user_query])

final_res= app.invoke(initial_state)
print(f"final_res : {final_res}")
