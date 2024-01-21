from gpt import *


client = create_client('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')
list_of_functions = [hello_world]
assistant = create_assistant(
                name="Test Assistant",
                instructions="No Matter what the user asks, reply with calling the function which will echo t heir response back to them! Only! And only call that function once & respond to the user, so the user can speak again!",
                tools=list_of_functions,
                model="gpt-3.5-turbo-16k",
                client=client
            )

thread = create_thread({"name": "Test Thread"}, client=client)

if not thread:
    print("Thread creation failed!")
    exit()

previous_message_id = ''
while True:
    user_input = input("User: ")

    message = create_thread_message(thread, "User", user_input, client)

    if not message:
        print("Message creation failed!")
        break

    run = run_thread(thread, assistant, client)
    if not run:
        print("Run creation failed!")
        break
    
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

    for message in messages:
        try:
            print(message.content[0].text.value)
        except:
            continue
