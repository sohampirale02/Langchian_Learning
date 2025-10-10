from typing import TypedDict
from typing import TypedDict,Annotated,Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
  name:str
  plan:list[str]
  user_query:str
  enhanced_query:str
  messages:Annotated[Sequence[BaseMessage],add_messages]

