import os
import PyPDF2

from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage,HumanMessage,AIMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated,Sequence
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

class AgentState(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]


def agent_node(state:AgentState)->AgentState:
    """Agent node which talks back and forth with HR and helps HR talk with the Resume"""
    print('inside agent_node')
    # print(f"state['messages'] : {state['messages']}")
    system_prompt = SystemMessage(content="You are AI assistant of HR manager who helps the HR talk with a resume, and uses read_pdf tool to retrive data from resume ask fr path of the resuem to the HR,after whole process is done and if HR is satisfied and wants to stop just return the string 'end' ONLY")
    response = llm.invoke([system_prompt]+state['messages'])
    state['messages']=[response]
    print('AI : ',response.content)
    return state

def decider(state:AgentState):
  messages=state["messages"]
  last_message=messages[-1]
  print("inside decider")
  if isinstance(last_message,AIMessage):
    if not last_message.tool_calls:
        if last_message=='end':
         return "end"
        else :
         return "hr_edge"
    else:
        return "tool_edge"
  else:
   return "hr_edge" 

def hr_node(state:AgentState)->AgentState:
   user_query = input("Enter something : ")
   state['messages']=[HumanMessage(content=user_query)]
   return state

def read_pdf(file_path):
    """Read text from a PDF file. Needs one filed called file_path to read pdf from"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


llm  = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.6,
    api_key=os.getenv("GEMINI_API_KEY")
).bind_tools([read_pdf])

graph = StateGraph(AgentState)
graph.add_node("agent_node",agent_node)
graph.add_node("tool_node",ToolNode(tools=[read_pdf]))
graph.add_node("hr_node",hr_node)
graph.add_edge(START,"agent_node")
graph.add_edge("tool_node","agent_node")
graph.add_edge("hr_node","agent_node")


graph.add_conditional_edges(
   "agent_node",
   decider,
   {
      "end":END,
      "hr_edge":"hr_node",
      "tool_edge":'tool_node'
   }
)

app =graph.compile()

initial_state = AgentState(messages=[HumanMessage(content ="Hello I am HR")])
response = app.invoke(initial_state)
print(f"final response : {response}")