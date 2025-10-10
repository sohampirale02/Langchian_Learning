from states import AgentState
from langchain_core.messages import AIMessage

def query_enhancer_decider(state:AgentState):
  messages = state['messages']
  last_message=messages[-1]

  if isinstance(last_message,AIMessage):
    if last_message.tool_calls:
      print(f"tools requested by query_enhancer : {last_message.tool_calls}")
      return "tool_node_edge"
    else :
      return "continue"

  return "continue"