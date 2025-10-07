from langgraph.graph import StateGraph,START,END
from typing import TypedDict

class AgentState(TypedDict):
  name:str
  num1:int
  num2:int
  operation:str
  ans:int

def addition_node(state:AgentState)->AgentState:
  ans= state["num1"]+state["num2"]
  print(f"answer of addtion is : {ans}")
  state["ans"]=ans
  return state

def substraction_node(state:AgentState)->AgentState:
  ans = state["num1"]-state["num2"]
  print(f"answer of substraction is : {ans}")
  state["ans"]=ans
  return state


def decider1(state:AgentState)->str:
  operator=state["operation"]

  if operator == "+":
    return "addition_edge"
  elif operator == '-':
    return "substraction_edge"



# graph = StateGraph(initial_state)
graph = StateGraph(AgentState)


graph.add_node("router",lambda state:state)
graph.add_edge(START,"router")

graph.add_node("addition_node",addition_node)
graph.add_node("substraction_node",substraction_node)

# graph.add_edge("addition_node",END)
# graph.add_edge("substraction_node",END)

# graph.add_edge("router","addition_node")
# graph.add_edge("router","substraction_node")

graph.add_conditional_edges(
  "router",
  decider1,
  {
    "addition_edge":"addition_node",
    "substraction_edge":"substraction_node"
  }
)

app = graph.compile()

initial_state= AgentState(name="soham",num1=10,num2=20,operation="-",ans=0)
result = app.invoke(initial_state)
print(f"result : {result}")



