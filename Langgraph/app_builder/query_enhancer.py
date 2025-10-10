from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts import system_prompt_query_enhancer
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage,HumanMessage
import os
from states import AgentState
from langgraph.prebuilt import ToolNode

#appn imports
from tools import ask_user

tools = [ask_user]
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    api_key=GEMINI_API_KEY 
).bind_tools(tools=tools)


query_enhancer_tool_node = ToolNode(tools=tools)

def query_enhancer_node(state:AgentState)->AgentState:
  print(f"state['messages'] : {state['messages']}")
  response = llm.invoke([SystemMessage(system_prompt_query_enhancer)]+state['messages'])
  state['messages']=[response]
  state["enhanced_query"]=response.content
  return state

