import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated,Sequence
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage,HumanMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
  messages:Annotated[Sequence[BaseMessage],add_messages]

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY : {GEMINI_API_KEY}")

@tool 
def add(num1:int,num2:int):
  """This tool adds two integer numbers"""
  print('inside add tool')
  return num1+num2

@tool
def substract(num1:int,num2:int):
  """This tool substracts 2 integer number"""
  return num1-num2

tools =[add,substract]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    api_key=GEMINI_API_KEY 
).bind_tools(tools=tools)

def ai_node(state:AgentState)->AgentState:
  system_prompt=SystemMessage(content="You are a friendly helpful humorous assistant")
  response = llm.invoke([system_prompt]+state["messages"])
  print(f"Response from LLM : {response.content}")
  state['messages']=[response]
  return state

def decider_ai_agent(state:AgentState):
  messages=state["messages"]
  last_message=messages[-1]

  if not last_message.tool_calls:
    return "end"
  else:
    return "continue"


tool_node = ToolNode(tools=tools)

graph=StateGraph(AgentState)
graph.add_node("ai_node",ai_node)
graph.add_node("tool_node",tool_node)
graph.add_edge(START,"ai_node")
graph.add_edge("tool_node","ai_node")


graph.add_conditional_edges(
  "ai_node",
  decider_ai_agent,
  {
    "end":END,
    "continue":"tool_node"
  }
)

app = graph.compile()

# initial_state=AgentState(messages=[HumanMessage(content='i.What is 2 +5 and ii.what is 7+7 and iii.then what is subtration of both the results?')])
initial_state=AgentState(messages=[HumanMessage(content='i.What is 2.3 + 4.5?')])


result = app.invoke(initial_state)
print(f"final_result : {result}")






