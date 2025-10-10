from langchain_core.tools import tool

@tool
def ask_user(query:str):
  """Tool which helps LLM to ask single question at a time to user and get their response via temrinal"""
  print('inside ask_user tool')
  print(f"Question : {query}\n")
  user_answer=input("User : ")
  return user_answer