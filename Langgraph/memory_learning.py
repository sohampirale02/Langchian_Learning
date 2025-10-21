from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,Annotated,Sequence
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver  
import os
import sqlite3
from langchain_core.messages import SystemMessage

# memory = SqliteSaver.from_conn_string("state.db",)  
# conn = sqlite3.connect("memory.db",check_same_thread=False)  
# conn.execute("CREATE TABLE IF NOT EXISTS summaries (thread_id TEXT PRIMARY KEY, summary TEXT)")

llm  = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.6,
    api_key=os.getenv('GEMINI_API_KEY')
)

memory = MemorySaver()

summary_memory_instances={}

class AgentState(TypedDict):
  messages : Annotated[Sequence[BaseMessage],add_messages]
  summary:str
  thread_id:str
  
def node(state:AgentState)->AgentState:
  system_prompt= SystemMessage(f"You are BEST friend of user, You GREAT and UNDERSTANDING humans and intweracting them as if you are one of them ! without talking overkill or cringe things you have PERFECT UNDERSTANDING of human interactions and bonds, You will also be given summary of previous interactions")
  human_message = state['messages'][-1]

  
  summary_memory = summary_memory_instances[state['thread_id']]
  
  memory_content = summary_memory.load_memory_variables({})['history']
  
  previous_summary = HumanMessage(content=f"Previous interactions: {memory_content}")  
  
  print(f'previous summary {previous_summary}')
  
  response = llm.invoke(
    [system_prompt,previous_summary,human_message]
  )
  
  summary_memory.save_context({"input": human_message.content}, {"output": response.content})
  
  print(f'AI : {response.content}')
  
  return {
    'messages':[response]
  }

graph = StateGraph(AgentState)
graph.add_node('node',node)
graph.add_edge(START,"node")
graph.add_edge('node',END)

app = graph.compile(checkpointer = memory)

while True:
  continue_chat=input("DO you want to chat again?")
  if continue_chat=='no':
    break
  
  thread_id = input('Enter your thread id : ')
  summary_memory = summary_memory_instances.get(thread_id)
  
  if not summary_memory:
    summary_memory= ConversationSummaryBufferMemory(
      llm=llm,
      max_token_limit=100,
      return_messages=True
    ) 
    summary_memory_instances[thread_id]=summary_memory
    
  config = {
    'configurable':{
      'thread_id':thread_id
    }
  }
  
  user_query = HumanMessage(content=input('You : '))
  
  initial_state=AgentState(
    messages=[user_query], 
    summary=summary_memory.load_memory_variables({})['history'] or "no summary yet",
    thread_id=thread_id
  )
  
  response = app.invoke(initial_state,config=config)
  
  # print(f'response from app : {response}')
  
print('BYE BYE')