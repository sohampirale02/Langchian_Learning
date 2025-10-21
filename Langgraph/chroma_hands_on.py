from langchain_cohere import CohereEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
import os

# Step 1: Load environment variables
load_dotenv()

# Step 2: Set up Cohere embeddings and Chroma
embeddings = CohereEmbeddings(model="embed-english-light-v3.0", cohere_api_key=os.getenv('COHERE_API_KEY'))
vector_store = Chroma(embedding_function=embeddings, collection_name="drive_notes", persist_directory="./chroma_db")

# # Step 3: Store Alex's drive notes
# notes = [
#     "Alex was happy on his evening drive and loved pop music.",
#     "Alex was stressed on this morning commute and loved jazz music.",
#     "Alex was stressed on this evening so he did yoga.",
#     "Alex loves eating ice cream."
# ]
# metadatas = [
#     {"user": "Alex", "mood": "happy", "date": "2025-10-21"},
#     {"user": "Alex", "mood": "stressed", "date": "2025-10-21"},
#     {"user": "Alex", "mood": "stressed", "date": "2025-10-21"},
#     {"user": "Alex", "mood": "happy", "date": "2025-10-21"}
# ]
# ids = ["note_1", "note_2",'note_3',"note_4"]

# vector_store.add_texts(texts=notes, metadatas=metadatas, ids=ids)
# vector_store.persist()  # Save to disk
# print("Stored Alex's drive notes in Chroma!")

# Step 4: Search for similar notes
user_input = "evening fullfillment"
# results = vector_store.similarity_search(user_input, k=1, filter={"mood": "stressed"})
results = vector_store.similarity_search(user_input, k=2)


# Step 5: Show the result
if results:
    print(f"results: {results}")
    
    # print(f"Found similar drive: {results[0].page_content}")
    # print(f"Metadata: {results[0].metadata}")
else:
    print("No similar drives found.")
