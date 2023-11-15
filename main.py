import os
from time import sleep
import openai
from openai import OpenAI

from flask import Flask, request, jsonify

print("Start")

# Connect to OpenAI API
openai.api_key = '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'
client = OpenAI(api_key=openai.api_key)

# Start the Flask App
app = Flask(__name__)

### Injest the file
file = client.files.create(file=open("internal.docx", "rb"),
                           purpose='assistants')

# Step 1: Create an Assistant
assistant = client.beta.assistants.create(
    instructions=
    "interactive chatbot is designed to provide you with information about our gym, assist you with membership-related inquiries, and make your experience with us seamless.",
    tools=[{
        "type": "retrieval"
    }],
    model="gpt-4-1106-preview",
    file_ids=[file.id])
print(f"Assistant Started with ID: {assistant.id}")


# For Setting the connection
@app.route('/start', methods=['GET'])
def initiate_conversation():
  print("Initiate a new Conversation with the Chatbot")
  # Step 2: Create a Thread
  thread = client.beta.threads.create()
  return jsonify({"thread_id": thread.id})


# For Starting the conversation
@app.route('/chat', methods=['POST'])
def chat():
  data = request.json
  thread_id = data.get('thread_id')
  user_input = data.get('message', '')

  # # Step 3: Add a message to the thread
  client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)

  # # Step 4: Run the Assistant
  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant.id)

  # #Step 5: Check the Run Status
  # # The code continuously checks the status of the assistant run.
  # # It waits until the run is completed before proceeding.
  while True:
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    print(f"Run status: {run.status}")
    if run.status == 'completed':
      break
    sleep(1)

  # Retrieve and return the latest message from the assistant
  messages = client.beta.threads.messages.list(thread_id=thread_id)
  response = messages.data[0].content[0].text.value

  return jsonify({"response": response})


# Start the SERVER
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
