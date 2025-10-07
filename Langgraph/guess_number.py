import random
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# Define the state
class AgentState(TypedDict):
    target: int
    counter: int
    lower_bound: int
    upper_bound: int
    guessed_num: int
    max_guess_limit:int
    success:bool

# Node to guess a random number
def guess_num_node(state: AgentState) -> AgentState:
    lower_bound = state["lower_bound"]
    upper_bound = state["upper_bound"]
    state["counter"]+=1
    print(f"upper_bound : {upper_bound} & lower_bound : {lower_bound}")
    guessed_num = random.randint(lower_bound, upper_bound)
    state["guessed_num"] = guessed_num  # Store the guessed number
    print(f"Guessed number: {guessed_num}")
  
    return state

def verifier (state:AgentState)->str:
  counter = state["counter"]
  max_guess_limit = state["max_guess_limit"]

  if counter > max_guess_limit:
    state["success"]=False
    return "end"
  else :
    guessed_num = state["guessed_num"]
    target = state["target"]

    if guessed_num == target:
      state["success"]=True
      return "end"
    else :
      if guessed_num < target:
        state["lower_bound"]=guessed_num+1
      else :
        state["upper_bound"]=guessed_num-1
      return "loop"

def start (state:AgentState)->AgentState:
  state["counter"]=0
  state["success"]=False
  return state

graph = StateGraph(AgentState)


graph.add_node("start", start)
graph.add_node("guess_num_node", guess_num_node)

graph.add_edge(START, "start")
graph.add_edge("start", "guess_num_node")

graph.add_conditional_edges(
  "guess_num_node",
  verifier,
  {
    "end":END,
    "loop":"guess_num_node"
  }
)

app = graph.compile()

initial_state = AgentState(
    target=4,  
    counter=0,
    lower_bound=1,
    upper_bound=20,
    guessed_num=0,
    max_guess_limit=5,
    success=False
)

# Run the graph
result = app.invoke(initial_state)
print(f"Result: {result}")