from lib import ensure_package_installed, install_packages, vprint
from typing import List, Callable

packages = ["openai==1.9.0"]
packages_not_installed = ensure_package_installed(packages, verbose=True)
install_packages(packages_not_installed, verbose=True)

from openai import OpenAI

client = OpenAI()

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

def convert_tool_to_json(tool: Callable, verbose: bool=False) -> dict:
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

    function_description = function_docs_segments[0]

    function_parameters = function_docs_segments[1]
    function_params_list = function_parameters.splitlines()
    function_params_json = {}

    for param in function_params_list:
        param_name = param.split(':')[0]
        param_type = param.split(':')[1]
        param_required = param.split(':')[2]
        param_description = param.split(':')[3]
        param_type_openai = python_to_openai_types.get(param_type, None)
        if param_type_openai is None:
            print(f'[ERROR] - We don\'t support custom types yet!')
            return {}

        param_description = param.split('-')[1]
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


def convert_tools_to_json(tools: List[Callable]) -> List[dict]:
    return [convert_tool_to_json(tool) for tool in tools]


def create_assistant(name: str, instructions: str, tools: List[Callable], model: str, verbose: bool=False):
    """
    Context:
        This function creates an assistant with the following parameters:

    Example:
        create_assistant()
    """
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=convert_tools_to_json(tools),
        model=model
    )

    return assistant

# Function to add function to assistant
# Function to remove function from assistant
# Function to retrieve assistant
# Function to delete assistant
# Function to list assistants
# Function to create thread
# Function to retrieve thread
# Function to delete thread
# Function to modify thread metadata
# Function to append message to thread
# Function to fetch messages from thread (Using pagination)
# Function to delete message from thread
# Function to list threads
# Function trigger thread to run
# Function to handle function event from thread message completion
# Function to convert other function output to readable human text
