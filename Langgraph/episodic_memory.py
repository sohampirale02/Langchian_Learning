from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List,Dict
import re
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,Annotated,Sequence
from langgraph.graph.message import add_messages
# from langgraph.checkpoint.sqlite import SqliteSaver  
import os
# import sqlite3
from pydantic import BaseModel,Field,validator
from langchain_core.messages import SystemMessage

llm  = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.6,
    api_key=os.getenv('GEMINI_API_KEY')
)

class AgentState(TypedDict):
  messages:Annotated[Sequence[BaseMessage],add_messages]

class NodeOutputStructure(BaseModel):
  continue_conversation:bool=Field(description=f'Deciding whether to continue the conversation, True : continue conversation False : User is satisfied or NOT RESPONDING so end this conversation')
  content:str=Field(description=f'Response from LLM to the user in text')
  
memory = MemorySaver()

def node(state:AgentState)->AgentState:
  user_query = input('You : ')
  user_query=HumanMessage(content = f'{user_query}')
  system_prompt=SystemMessage(content=f"You are friendly helpful assistant of the user, interact with him in friendly way,YOu wil also be given  previous conversations, return 'end' when user wnats to end the conversation and NO OTHER word in response!")
  messages = [system_prompt,user_query]
  
  if len(state['messages'])>3:
    previous_interactions=state['messages'][-3::] 
    messages = messages + [HumanMessage(content=f"previous_interactions : {previous_interactions}")]
    
  elif len(state['messages'])!=0 :
    previous_interactions=state['messages']
    messages= messages + [HumanMessage(content=f"previous_interactions : {previous_interactions}")]
    
  # messages = messages +[ HumanMessage(content=f'Previous conversations : {state['messages']}')]
  
  # print(f"messages for invoking llm : {messages}")
  response = llm.invoke(messages)
  
  print(f'AI : {response.content}')
  return {
    'messages':[user_query,response]
  }
  
  
def node_decider(state:AgentState):
  last_message = state['messages'][-1]
  
  if last_message.content.strip() == 'end':
    return "end"
  else:
    return "node"
  


agent_graph = StateGraph(AgentState)

agent_graph.add_node("node",node)
agent_graph.add_edge(START,"node")
agent_graph.add_conditional_edges(
  "node",
  node_decider,
  {
    "node":"node",
    "end":END
  }
)

agent_app = agent_graph.compile(checkpointer=memory)
  
  
class EpisodicState(TypedDict):
  messages:Annotated[Sequence[BaseMessage],add_messages]

# class EpisodicOutputStructure(BaseModel):
#   concise_summary:str=Field(description=f"Concise Summary: Summarize the conversation in 1-2 sentences, focusing on user’s mood, actions, preferences, and outcomes.Example: Vaibhav was stressed, loved jazz, hated rock on commute.”")
#   key_details : str=Field(description=f"Extract user’s mood, preferences (e.g., music, routes), and what worked/didn’t")
#   metadata:dict=Field(description=f"""dictionary of metadata Include date, user name, and mood as metadata.”Example: dict -> date: "2025-10-21", user: "Alex", mood: "stressed""")
#   tags:list[str]=Field(description=f"WIll be used for RAG,Suggest keywords for filtering (e.g., mood, actions). that will be used for RAG!")
  
  
class EpisodicOutputStructure(BaseModel):
    concise_summary: str = Field(
        description="A 1-2 sentence summary of the conversation, focusing on user’s mood, actions taken, preferences, and outcomes. Example: 'Alex was stressed on morning commute, loved jazz, hated rock.'",
        min_length=10,
        max_length=200
    )
    key_details: Dict[str, str] = Field(
        description="Key details as a dictionary. Include 'mood' (e.g., 'stressed'), 'preferences' (e.g., 'loves jazz, hates rock'), 'actions' (e.g., 'suggested Highway B'), and 'outcome' (e.g., 'worked well'). Example: {'mood': 'stressed', 'preferences': 'loves jazz, hates rock', 'actions': 'suggested Highway B', 'outcome': 'worked well'}"
    )
    metadata: Dict[str, str] = Field(
        description="Metadata with required keys: 'date' (YYYY-MM-DD), 'user' (name), 'mood' (e.g., 'stressed', 'happy'). Example: {'date': '2025-10-21', 'user': 'Alex', 'mood': 'stressed'}"
    )
    tags: List[str] = Field(
        description="Keywords for RAG filtering, e.g., mood, actions, preferences. Example: ['stress', 'jazz', 'rock_hate', 'commute']",
        min_items=1
    )
    

    
def episodic_memory_creator(state:EpisodicState)->EpisodicState:
  previous_conversations = state['messages']
  system_prompt = SystemMessage(content="""
  You are an expert at understanding human conversations for a car assistant AI, CarBuddy. Your job is to create an episodic memory from a given conversation, summarizing a user's drive. Generate a structured output with:
  - concise_summary: 1-2 sentences on the user’s mood, actions taken, preferences, and outcomes (e.g., 'Alex was stressed, loved jazz, hated rock on commute').
  - key_details: A dictionary with 'mood' (e.g., 'stressed'), 'preferences' (e.g., 'loves jazz, hates rock'), 'actions' (e.g., 'suggested Highway B'), and 'outcome' (e.g., 'worked well').
  - metadata: A dictionary with 'date' (YYYY-MM-DD), 'user' (name), and 'mood' (e.g., 'stressed').
  - tags: A list of keywords for filtering (e.g., ['stress', 'jazz', 'commute']).
  If the conversation is short or unclear, note missing details in the summary. Output as valid JSON.
    
    IMP:Main job you have is understanding that HUMAN with empathy and expertise in HUMAN behaviourals
  """)
  human_msg = HumanMessage(content=f"previous_interactions : {previous_conversations}")
  llm_episodic_output = llm.with_structured_output(EpisodicOutputStructure)
  
  messages = [system_prompt,human_msg]
  structured_episodic_response = llm_episodic_output.invoke(messages)
  print(f'Output from episodic_memory_creator : {structured_episodic_response}')
  return state

  
episodic_graph = StateGraph(EpisodicState)
episodic_graph.add_node("episodic_memory_creator",episodic_memory_creator)
episodic_graph.add_edge(START,"episodic_memory_creator")
episodic_graph.add_edge("episodic_memory_creator",END)
episodic_app= episodic_graph.compile(checkpointer=memory)
  
while True:
  continue_again=input(f'1 : continue 0 : end\nYour choice : ') 
  if continue_again == '0':
    break

  thread_id = input('Enter thread_id : ')
  config = {
    "configurable":{
      "thread_id":thread_id
    }
  }
  
  initial_state= AgentState(
    messages=[]
  )
  
  agent_app_resoponse= agent_app.invoke(initial_state,config=config)
  print(f'agent_app_response : {agent_app_resoponse}')
  
  
  print("=== Retrieving State After Execution ===")
  checkpoint = memory.get_tuple(config) 
  if checkpoint:
      state = checkpoint.checkpoint['channel_values']
      episodic_app.invoke(state,config=config)
  else:
      print("No checkpoint found.")
    
  