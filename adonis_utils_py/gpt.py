true = True
false = False

from lib import ensure_package_installed, install_packages, vprint
from typing import List, Callable, Dict, Optional, Union

packages = ["openai==1.9.0", "yaml"]
packages_not_installed = ensure_package_installed(packages, verbose=True)
install_packages(packages_not_installed, verbose=True)

from openai import OpenAI
import openai.types.beta as openai_types
import openai.types.shared as openai_shared_types
import yaml


client = OpenAI(api_key="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")

def hello_world(message: str) -> str:
    """
    This is a test function that returns "Hello World"
    ----
    message: str: True: The message to return
    """
    return message


# TODO:
# Function to create assistant
python_to_openai_types = {
    "str": "string",
    "int": "number",
    "float": "number",
    "bool": "boolean",
    "list": "list",
    "dict": "object",
    "tuple": "list",
    "set": "list",
    "frozenset": "list",
    "NoneType": "null"
}

def convert_tool_to_json(tool: Callable, verbose: bool=False) -> Dict[str, str]:
    """
    Context:
        It is hard to manage a massive amount of tools and their documentation, hence we are making docstrings the source of truth for our tools.

    Example:
        DOCSTRING Format:
            description \n on \n any \n amount \n of \n lines
            ----\n ( 5 dashes )
            param1: str: True: description on one line
            param2: int: True: description on one line
            param3: float: True: description on one line
            param4: bool: True: description on one line

        convert_tool_to_json(tool, verbose=True)

    OUTPUT:
        convert_tool_to_json(tool, verbose=True)
    """
    
    function_docstring = tool.__doc__
    
    if function_docstring is None:
        vprint(f'[ERROR] - Function {tool.__name__} does not have a docstring', verbose)
        return {}

    function_name = tool.__name__

    function_docs_segments = function_docstring.split("----\n")

    function_description = function_docs_segments[0].strip()

    function_parameters = function_docs_segments[1]
    function_params_list = function_parameters.splitlines()
    function_params_json = {}

    for param in function_params_list:
        if param.strip() == "":
            continue
        
        param_name = param.split(':')[0].strip()
        param_type = param.split(':')[1].strip()
        param_required = param.split(':')[2].strip()
        param_description = param.split(':')[3].strip()
        param_type_openai = python_to_openai_types.get(param_type, None)
        if param_type_openai is None:
            print(f'[ERROR] - We don\'t support custom types yet!')
            return {}

        function_params_json[param_name] = { 
                        "type": param_type_openai,
                        "description": param_description,
                        "required": param_required == "True"
                }
    
    fixed_function_params_json = {}
    required_function_params_json = []
    for key, value in function_params_json.items():
        if value["required"]:
            required_function_params_json.append(key)

        del value["required"]
        fixed_function_params_json[key] = value

        

    function_output = {
            "type": "function",
            "function": {
                "name": function_name,
                "description": function_description,
                "parameters": {
                    "type": "object",
                    "properties": fixed_function_params_json
                    }
                }
            }
    
    return function_output


def convert_tools_to_json(tools: List[Callable]) -> List[Dict[str, str]]:
    """
    Context:
        It is hard to manage a massive amount of tools and their documentation, hence we are making docstrings the source of truth for our tools.

    Example:
        DOCSTRING Format:
            description \n on \n any \n amount \n of \n lines
            ----\n ( 5 dashes )
            param1: str: True: description on one line
            param2: int: True: description on one line
            param3: float: True: description on one line
            param4: bool: True: description on one line
        convert_tools_to_json([tool1, tool2, tool3])

    Output:
        convert_tools_to_json([tool1, tool2, tool3])
    """
    return [convert_tool_to_json(tool) for tool in tools]


def create_assistant(name: str, instructions: str, tools: List[Callable], model: str, verbose: bool=False) ->  openai_types.assistant.Assistant:
    """
    Context:
        This function creates an assistant.

    Example:
        create_assistant(
                name="Test Assistant",
                instructions="No Matter what the user asks, reply with 'Hello World' Only!",
                tools=convert_tools_to_json([hello_world]),
                model="gpt-3.5-turbo-16k"

    Output:
        retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S)

    """

    # TODO: Fix this type complaint
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=convert_tools_to_json(tools),
        model=model
    )

    return assistant


# TODO: Remove this
# # Example usage:
# assistant = create_assistant(
#         name="Test Assistant",
#         instructions="No Matter what the user asks, reply with 'Hello World' Only!",
#         tools=[hello_world],
#         model="gpt-3.5-turbo-16k"
# )

# print(assistant.id)

# Function to retrieve assistant
def retrieve_assistant(assistant_id: str) -> openai_types.assistant.Assistant:
    """
    Context:
        This function retrieves an assistant using its id.

    Example:
        retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S)

    Output:
        retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S)

    """
    return client.beta.assistants.retrieve(assistant_id)

# Function to delete assistant
def delete_assistant(assistant: openai_types.assistant.Assistant) -> bool:
    """
    Context:
        This function deletes an assistant using its Assistant Object.

    Example:
        delete_assistant(retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S))

    Output:
        True or False, depending on whether the assistant was deleted or not.
    """
    
    try:
        return client.beta.assistants.delete(assistant.id).deleted
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return False

    

# Function to list assistants
def list_assistants() -> List[openai_types.assistant.Assistant]:
    """
    Context:
        This function lists all assistants.
    Example:
        list_assistants()
    Output:
        list_assistants()
    """
    try:
        return client.beta.assistants.list(limit=100).data
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return []


# Function to create thread
def create_thread(metadata: Dict[str, str]) -> Optional[openai_types.thread.Thread]:
    """
    Context:
        This function creates a thread.
    Example:
        create_thread({"name": "Test Thread"})
    Output:
        create_thread({"name": "Test Thread"})
    """
    try:
        return client.beta.threads.create(metadata=metadata)
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return None

# Function to retrieve thread
def retrieve_thread(thread_id: str) -> Optional[openai_types.thread.Thread]:
    """
    Context:
        This function retrieves a thread.
    Example:
        retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S")
    Output:
        retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S")
    """
    try:
        return client.beta.threads.retrieve(thread_id)
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return None

# Function to delete thread
def delete_thread(thread: openai_types.thread.Thread) -> bool:
    """
    Context:
        This function deletes a thread.
    Example:
        delete_thread(retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))
    Output:
        delete_thread(retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))
    """
    try:
        return client.beta.threads.delete(thread.id).deleted
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return False

# Function to modify thread metadata
def modify_thread_metadata(thread: openai_types.thread.Thread, metadata: Dict[str, str]) -> Optional[openai_types.thread.Thread]:
    """
    Context:
        This function modifies a thread's metadata.
    Example:
        modify_thread_metadata(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), metadata={"name": "New Name"})
    Output:
        modify_thread_metadata(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), metadata={"name": "New Name"})
    """
    try:
        return client.beta.threads.update(thread.id, metadata=metadata)
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return None

# Function to append message to thread
def create_thread_message(thread: openai_types.thread.Thread, role: str, content: str) -> Optional[openai_types.thread.ThreadMessage]:
    try:
        message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role='user',
                content=f"SYSTEM MESSAGE::::This message was sent from {role}::::\n" + content
            )
        return message
    except Exception as e:
        return None

# Function to fetch messages from thread (Using pagination)
def retrieve_thread_messages(thread: openai_types.thread.Thread) -> List[openai_types.thread.ThreadMessage]:
    try:
        return client.beta.threads.messages.list(thread_id=thread.id, limit=100000000000000).data
    except:
        return []

# Function trigger thread to run
def run_thread(thread: openai_types.thread.Thread, assistant: openai_types.assistant.Assistant) -> Optional[openai_types.thread.run]
    try:
        run = client.beta.threads.runs.create(
          thread_id=thread.id,
          assistant_id=assistant.id,
          instructions="Please address the user as Jane Doe. The user has a premium account."
        )
        return run
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return None

def retrieve_run(run: openai_types.thread.run, thread: openai_types.thread.Thread) -> Optional[openai_types.thread.run]:
    try:
        return client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread.id)
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return None

def retrieve_run(run: openai_types.thread.run, thread: openai_types.thread.Thread) -> Optional[openai_types.thread.run]:
    try:
        return client.beta.threads.runs.cancel(run_id=run.id, thread_id=thread.id)
    except Exception as e:
        vprint(f'[ERROR] - {e}')
        return None


def run_execute_required_function(run: openai_types.thread.run, functions: List[Callable]) -> Optional[openai_types.thread.run]:
    try:
        # TODO: Get the function we need to run
        # TODO: Run it
        # TODO: Set the output to the run & append to the thread
        ...
    except Exception:
        return None


# Function to handle function event from thread message completion
openai_states = ['queued', 'require_action', 'in_progress', 'cancelling', 'expired', 'completed', 'failed', 'cancelled']
def manage_run_state(run: openai_types.thread.run) -> Union[bool, str, None]:
    run_state = run.status

    switcher = {
        'queued': None,
        'require_action': 'REQUIRED',
        'in_progress': None,
        'cancelling': None,
        'expired': False,
        'completed': True,
        'failed': False,
        'cancelled': None
    }
    
    return switcher.get(run_state)
    
# Function to convert other function output to readable human text
def convert_json_to_yaml(json: Dict) -> str:
    """
    Context:
        This function converts a json to yaml.
    Example:
        convert_json_to_yaml({"name": "Test"})
    Output:
        convert_json_to_yaml({"name": "Test"})
    """

    return '\n'.join([f"{key}: {value if type(value) != 'dict' else convert_json_to_yaml(value)}" for key, value in json.items()])
