import time

from lib import ensure_package_installed, install_packages, vprint
packages = ["flask"]
packages_not_installed = ensure_package_installed(packages, verbose=True)
install_packages(packages_not_installed, verbose=True)


from gpt import *
from flask import Flask, request, jsonify


client= create_client('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')
app = Flask(__name__)


@app.route("/completion", methods=["POST"])
def completion():
    data = request.json

    thread_id = data['thread_id']
    assistant_id = data['assistant_id']
    previous_message_id = data['previous_message_id']
    user_input = data['message']
    role = data['role']

    assistant = retrieve_assistant(assistant_id, client)
    thread = retrieve_thread(thread_id, client)
    list_of_functions = [hello_world]
    assistant = create_assistant(
                    name="Test Assistant",
                    instructions="No Matter what the user asks, reply with calling the function which will echo t heir response back to them! Only! And only call that function once & respond to the user, so the user can speak again!",
                    tools=list_of_functions,
                    model="gpt-3.5-turbo-16k",
                    client=client
                )

    if not thread:
        print("Thread creation failed!")
        return jsonify({"error": "Thread creation failed!"})

    user_input = input("User: ")

    message = create_thread_message(thread, role, user_input, client)

    if not message:
        print("Message creation failed!")
        return jsonify({"error": "Message creation failed!"})

    run = run_thread(thread, assistant, client)
    if not run:
        print("Run creation failed!")
        return jsonify({"error": "Run creation failed!"})
    
    while True:
        time.sleep(1)
        run = retrieve_run(run, thread, client)
        run_state = manage_run_state(run)
        
        if run_state == 'REQUIRED':
            run_run_functions(thread, run, list_of_functions, client)
            continue
        elif run_state == True:
            break
        elif run_state == False:
            continue

    messages = retrieve_thread_messages(thread, client)
    previous_message_id = messages[0].id
    messages.reverse()
    
    previous_message_index = 0
    if previous_message_id != '':
        previous_message_index = [message.id for message in messages].index(previous_message_id)

    messages = messages[previous_message_index:]
    
    messages = []
    for message in messages:
        try:
            messages.append(
                        {
                            'role': message.role,
                            'content': message.content[0].text.value
                        }
                    )
        except:
            pass
    
    return jsonify({"messages": messages})

@app.route("/create_thread", methods=["POST"])
def create_thread():
    data = request.json
    thread = create_thread(data['metadata'], client=client)
    if not thread:
        print("Thread creation failed!")
        return jsonify({"error": "Thread creation failed!"})
    return jsonify({"thread_id": thread.id})

@app.route("/list_assistants", methods=["GET"])
def list_assistants_flsk():
    assistants = list_assistants(client)
    if not assistants:
        print("No assistants found!")
        return jsonify({"error": "No assistants found!"})
    return jsonify({"assistants": [assistant.id for assistant in assistants]})

if __name__ == "__main__":
    app.run(debug=True)
