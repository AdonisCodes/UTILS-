true = True
false = False

from lib import ensure_package_installed, install_packages, vprint
from typing import List, Callable, Dict, Optional, Union, TypedDict
import json

packages = ["openai==1.9.0"]
packages_not_installed = ensure_package_installed(packages, verbose=True)
install_packages(packages_not_installed, verbose=True)

from openai import OpenAI
import openai.types.beta as openai_types
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput
from openai.types.beta.threads import ThreadMessage, Run


# Type Declerations
ASSISTANT = openai_types.assistant.Assistant
THREAD = openai_types.thread.Thread
THREAD_MESSAGE = ThreadMessage
RUN = Run

# Constants
openai_states = ['queued', 'require_action','requires_action' 'in_progress', 'cancelling', 'expired', 'completed', 'failed', 'cancelled']
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
def hello_world(input: str) -> Dict[str, str]:
    """
    This is a dummy function to test the library.
    -----\n
    input: str: True: The input to the function
    """
    print('worked', input)
    return {"output": input}


def create_client(api_key: str, verbose: bool=False) -> OpenAI:
    """
    Context:
        This creates a client which you can use for all the gpt related functions.

    Example:
        create_client("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")

    Output:
       OpenAI() instance

    Reference:
        https://platform.openai.com/docs/assistants/overview
    """
    client = OpenAI(api_key=api_key)
    vprint(f'[INFO] - Created client {client}', verbose)
    return client


def convert_tool_to_json(tool: Callable, verbose: bool=False, deliminer: str = '-----\n') -> Dict:
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

    Reference:
        https://platform.openai.com/docs/guides/function-calling
    """
    
    function_docstring = tool.__doc__
    if function_docstring is None:
        vprint(f'[ERROR] - Function {tool.__name__} does not have a docstring', verbose)
        return {}

    function_name = tool.__name__
    function_docs_segments = function_docstring.split(deliminer)
    function_description = function_docs_segments[0].strip()
    function_parameters = function_docs_segments[1]
    function_params_list = function_parameters.splitlines()
    function_params_json = {}
    
    for param in function_params_list:
        vprint(f'[INFO] - {param}', verbose)
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
    
    vprint('[INFO] - converting to openai type', verbose)
    fixed_function_params_json = {}
    required_function_params_json = []
    for key, value in function_params_json.items():
        if value["required"]:
            required_function_params_json.append(key)

        del value["required"]
        fixed_function_params_json[key] = value

        
    
    vprint('[INFO] - converting to openai type', verbose)
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
    
    vprint(f'[INFO] - {function_output}')
    return function_output


def convert_tools_to_json(tools: List[Callable], verbose: bool=False) -> List:
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

    Reference:
        https://platform.openai.com/docs/guides/function-calling
    """
    vprint('[INFO] - Converting tools to json', verbose)
    return [convert_tool_to_json(tool) for tool in tools]


def create_assistant(name: str, instructions: str, tools: List[Callable], model: str, client: OpenAI, verbose: bool=False) ->  ASSISTANT:
    """
    Context:
        This function creates an assistant.

    Example:
        create_assistant(
                name="Test Assistant",
                instructions="No Matter what the user asks, reply with 'Hello World' Only!",
                tools=convert_tools_to_json([hello_world]),
                model="gpt-3.5-turbo-16k",
                client=client)

    Output:
        retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S)
    
    Reference:
        https://platform.openai.com/docs/assistants/overview/step-1-create-an-assistant
    """

    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=convert_tools_to_json(tools),
        model=model
    )

    vprint(f'[INFO] - Created assistant {assistant}', verbose)
    return assistant


def retrieve_assistant(assistant_id: str, client: OpenAI, verbose: bool=False) -> ASSISTANT: 
    """
    Context:
        This function retrieves an assistant using its id.

    Example:
        retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S)

    Output:
        retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S)
    
    Reference:
        https://platform.openai.com/docs/assistants/overview/step-1-create-an-assistant
    """
    
    vprint(f"[INFO] - Retrieving assistant {assistant_id}", verbose)
    return client.beta.assistants.retrieve(assistant_id)


def delete_assistant(assistant: ASSISTANT, client: OpenAI, verbose: bool=False) -> bool:
    """
    Context:
        This function deletes an assistant using its Assistant Object.

    Example:
        delete_assistant(retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S))

    Output:
        True or False, depending on whether the assistant was deleted or not.

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-1-create-an-assistant
    """
    
    try:
        vprint(f'[INFO] - Deleting assistant {assistant}', verbose)
        return client.beta.assistants.delete(assistant.id).deleted
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return False
    

def list_assistants(client: OpenAI, verbose: bool=False) -> List[ASSISTANT]:
    """
    Context:
        This function lists all the assistants for the openai organization / api key you used.

    Example:
        list_assistants()

    Output:
        list_assistants()

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-1-create-an-assistant
    """
    try:
        vprint(f'[INFO] - Listing assistants', verbose)
        return client.beta.assistants.list(limit=100).data
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return []


def create_thread(metadata: Dict[str, str], client: OpenAI, verbose: bool=False) -> Optional[THREAD]:
    """
    Context:
        This function creates a thread to use for messaging.

    Example:
        create_thread({"name": "Test Thread"}, client=client)

    Output:
        create_thread({"name": "Test Thread"}, client=client)

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-2-create-a-thread
    """
    try:
        vprint(f'[INFO] - Creating thread with metadata {metadata}', verbose)
        return client.beta.threads.create(metadata=metadata)
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return None


def retrieve_thread(thread_id: str, client: OpenAI, verbose: bool=False) -> Optional[THREAD]:
    """
    Context:
        This function retrieves a thread.

    Example:
        retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S")

    Output:
        retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S")

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-2-create-a-thread
    """
    try:
        vprint(f'[INFO] - Retrieving thread {thread_id}', verbose)
        return client.beta.threads.retrieve(thread_id)
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return None


def delete_thread(thread: THREAD, client: OpenAI, verbose: bool=False) -> bool:
    """
    Context:
        This function deletes a thread.

    Example:
        delete_thread(retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Output:
        delete_thread(retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-2-create-a-thread
    """
    try:
        vprint(f'[INFO] - Deleting thread {thread}', verbose)
        return client.beta.threads.delete(thread.id).deleted
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return False



def modify_thread_metadata(thread: THREAD, metadata: Dict[str, str], client: OpenAI, verbose: bool=False) -> Optional[THREAD]:
    """
    Context:
        This function modifies a thread's metadata.

    Example:
        modify_thread_metadata(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), metadata={"name": "New Name"})

    Output:
        modify_thread_metadata(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), metadata={"name": "New Name"})

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-2-create-a-thread
    """
    try:
        vprint(f'[INFO] - Modifying thread {thread} with metadata {metadata}', verbose)
        return client.beta.threads.update(thread.id, metadata=metadata)
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return None



def create_thread_message(thread: THREAD, role: str, content: str, client: OpenAI, verbose: bool=False) -> Optional[THREAD_MESSAGE]:
    """
    Context:
        This function appends an ThreadMessage to an openai thread

    Example:
        create_thread_message(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), role="User", content="Hello World")

    Output:
        create_thread_message(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), role="User", content="Hello World")

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-3-add-a-message-to-a-thread

    """
    try:
        message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role='user',
                content=f"SYSTEM MESSAGE::::This message was sent from {role}::::\n" + content
            )

        vprint(f'[INFO] - Created message {message}', verbose)
        return message
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return None



def retrieve_thread_messages(thread: THREAD, client: OpenAI, after: Optional[str]=None, verbose: bool=False) -> List[THREAD_MESSAGE]:
    """
    Context:
        This function retrieves all messages from an openai thread ( Or the after id you define)

    Example:
        retrieve_thread_messages(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Output:
        retrieve_thread_messages(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-3-add-a-message-to-a-thread
    """
    try:
        if after:
            vprint(f'[INFO] - Retrieving messages from thread {thread} after {after}', verbose)
            return client.beta.threads.messages.list(thread_id=thread.id, limit=100000000000000, after=after).data
        else:
            vprint(f'[INFO] - Retrieving messages from thread {thread}', verbose)
            return client.beta.threads.messages.list(thread_id=thread.id).data
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return []


def run_thread(thread: THREAD, assistant: ASSISTANT, client: OpenAI, verbose: bool=False) -> Optional[RUN]:
    """
    Context:
        An openai thread needs to be forced to run in order for it to give a response, this gives more control.

    Example:
        run_thread(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), assistant=retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S), client=client)

    Output:
        run_thread(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), assistant=retrieve_assistant(asst_XYJLoLEhgvcuGhYHoUNiIh0S), client=client)

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-4-run-the-assistant
    """
    try:
        run = client.beta.threads.runs.create(
          thread_id=thread.id,
          assistant_id=assistant.id,
        )

        vprint(f'[INFO] - Created run {run}', verbose)
        return run
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return None


def retrieve_run(run: Optional[RUN], thread: THREAD, client: OpenAI, verbose: bool=False) -> Optional[RUN]:
    """
    Context:
        This function retrieves the run object.

    Example:
        retrieve_run(run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"), thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Output:
        retrieve_run(run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"), thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-5-check-the-run-status
    """
    if not run:
        vprint(f'[ERROR] - Run is None', verbose)
        return None

    try:
        vprint(f'[INFO] - Retrieving run {run}', verbose)
        return client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread.id)
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return None


def cancel_run(run: RUN, thread: THREAD, client: OpenAI, verbose: bool=False) -> Optional[RUN]:
    """
    Context:
        This function cancels the run object.

    Example:
        cancel_run(run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"), thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Output:
        cancel_run(run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"), thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-5-check-the-run-status
    """
    try:
        vprint(f'[INFO] - Cancelling run {run}', verbose)
        return client.beta.threads.runs.cancel(run_id=run.id, thread_id=thread.id)
    except Exception as e:
        vprint(f'[ERROR] - {e}', verbose)
        return None



def submit_function_outputs(thread: THREAD, run: RUN, client: OpenAI, tool_outputs: List[ToolOutput], verbose: bool=False) -> Run:
    """
    Context:
        This function submits the function outputs to the thread.

    Example:
        submit_function_outputs(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"), client=client, tool_outputs=[{"tool_call_id": "tool_1", "output": "Hello World"}])

    Output:
        submit_function_outputs(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"), client=client, tool_outputs=[{"tool_call_id": "tool_1", "output": "Hello World"}])

    Reference:
        https://platform.openai.com/docs/assistants/overview/step-5-check-the-run-status
    """
    submit_run: Run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )
    
    vprint(f'[INFO] - Submitted run {submit_run}', verbose)
    return submit_run


def run_run_functions(thread: THREAD, run: Optional[RUN], functions: List[Callable], client: OpenAI, verbose: bool=False):
    """
    Context:
        This function runs the 3rd party functions you have added.

    Example:
        run_run_functions(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"), functions=[hello_world], client=client)

    Output:
        run_run_functions(thread=retrieve_thread(thread_id="thread_XYJLoLEhgvcuGhYHoUNiIh0S"), run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"), functions=[hello_world], client=client)

    Reference:
        https://platform.openai.com/docs/guides/function-calling
    """
    if not run:
        vprint(f'[ERROR] - Run is None', verbose)
        return None

    if run.required_action and run.required_action.type == 'submit_tool_outputs':
        openai_funcs = run.required_action.submit_tool_outputs
        tool_outputs: List[ToolOutput] = []
        function_names_objs = {f.__name__: f for f in functions}
        for function in openai_funcs.tool_calls:
            if not function.function or function.function.arguments is None:
                continue

            tool_output = ToolOutput(
                tool_call_id=function.id,
                output=convert_json_to_text(function_names_objs[function.function.name](**json.loads(function.function.arguments))
            ))

            tool_outputs.append(tool_output)

        vprint(f"Submitting tool outputs {tool_outputs}", verbose)
        submit_function_outputs(thread, run, client, tool_outputs)


def manage_run_state(run: Optional[RUN], verbose: bool=False) -> Union[bool, str, None]:
    """
    Context:
        This is basically a massive switch statement to determine what to do with the run.

    Example:
        manage_run_state(run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Output:
        manage_run_state(run=retrieve_run(run_id="run_XYJLoLEhgvcuGhYHoUNiIh0S"))

    Reference:
        NONE
    """
    if not run:
        vprint(f'[ERROR] - Run is None', verbose)
        return False

    run_state = run.status
    
    
    switcher = {
        'queued': None,
        'require_action': "REQUIRED",
        'requires_action': 'REQUIRED',
        'in_progress': None,
        'cancelling': None,
        'expired': False,
        'completed': True,
        'failed': False,
        'cancelled': None
    }
    
    vprint(f'[INFO] - Run State {run_state}', verbose)
    return switcher.get(run_state)
 

def convert_json_to_text(json: Dict, verbose: bool=False) -> str:
    """
    Context:
        This function converts a json to human readable text.

    Example:
        convert_json_to_yaml({"name": "Test"})

    Output:
        convert_json_to_yaml({"name": "Test"})
    """
    
    vprint(f'[INFO] - Converting json to text {json}', verbose)
    return '\n'.join([f"{key}: {value if type(value) != 'dict' else convert_json_to_text(value)}" for key, value in json.items()])

