# Import necessary libraries
import subprocess
import threading
import ollama
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

# Define color codes for terminal output
class Color:
    """
    A class to define ANSI color codes for terminal output.
    """
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BLUE = '\033[94m'
    PINK = '\033[95m'


def ollama_api_call(os_name, command, model_name):
    """
    Calls the Ollama API to convert user queries into command-line commands.

    Parameters:
    os_name (str): The operating system name.
    command (str): The user query to convert.
    model_name (str): The model name to use for the API call.

    Returns:
    str: The generated command-line command.
    """
    logging.debug(f"Calling Ollama API with OS: {os_name}, command: {command}, and model: {model_name}")
    stream = ollama.chat(
        model=model_name,
        options={'temperature': 0.1},
        messages=[{'role': 'user', 'content': f'I am using {os_name} operating system which does not have any extentions installed and I want to Convert the user query: {command} to commandline / terminal code. Only output one line of terminal command please. Do not add any other text as the intention is to copy paste this generated output directly in terminal and run.'}],
        stream=True,
    )
    logging.debug("Ollama API call completed")
    
    stream_data = []
    for chunk in stream:
        stream_data.append(chunk['message']['content'])
        print(f"{Color.BLUE}{chunk['message']['content']}{Color.RESET}", end='', flush=True)
    
    strdata = ''.join([chunk for chunk in stream_data]).replace("`", "").replace("```sh", "").replace("\n", "").replace("```bash", "")
    print(f"\n{Color.BLUE}Finished.\nGenerated: {strdata}\n{Color.RESET}")
    
    return strdata.strip().replace('`', '')


def echo_and_execute(command, os_name, model_name):
    """
    Executes a command generated by the Ollama API and handles user confirmation.

    Parameters:
    command (str): The command to execute.
    os_name (str): The operating system name.
    model_name (str): The model name used for the API call.
    """
    logging.info(f"Executing command: {command} on OS: {os_name}")
    try:
        command_to_execue = ollama_api_call(os_name, command, model_name)
        confirm = input(f"Generated command is: {Color.CYAN}'{command_to_execue}', shall we continue? (Y/N):{Color.RESET}# ").strip().lower()
        if confirm.lower() in ['y', 'yes', 'yup']:
            result = subprocess.run(command_to_execue, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info(f"Command executed: {command_to_execue}")
        else:
            logging.warning("Command execution canceled by user")
            return
        output = result.stdout.decode().strip()
        error = result.stderr.decode().strip()
        if output:
            logging.debug(f"Command output: {output}")
            print(f"\n{Color.GREEN}# Output:{Color.RESET}\n{Color.PINK}{output}{Color.RESET}")
        if error:
            logging.error(f"Command error: {error}")
            print(f"\n{Color.RED}Error: {error}{Color.RESET}")
    except Exception as e:
        logging.exception(f"An exception occurred: {e}")
        print(f"{Color.RED}An exception occurred while executing the command: {e}{Color.RESET}", file=sys.stderr)


def custom_cmd(os_name, model_name):
    """
    Starts a custom command prompt for executing user queries.

    Parameters:
    os_name (str): The operating system name.
    model_name (str): The model name to use for the API call.
    """
    logging.info(f"Starting custom command prompt for {os_name} with model {model_name}")
    print(f"{Color.CYAN}Welcome to the Initial Terminal command prompt for {os_name} with model {model_name}!\n Ollama with {model_name} LLM running locally for inference\n{Color.RESET}\n Type quit/exit to exit")

    while True:
        try:
            input_str = input(f"{Color.GREEN}_____________\nCommand to execute :\n{Color.RESET}# ")
            
            if "exit" in input_str.lower() or "quit" in input_str.lower():
                logging.info("Exiting custom command prompt")
                print(f"{Color.GREEN}Exiting the custom command prompt.{Color.RESET}")
                break

            echo_and_execute(input_str, os_name, model_name)

        except KeyboardInterrupt:
            logging.info("Exiting custom command prompt due to keyboard interrupt")
            print("Exiting the custom command prompt.")
            break


def start_custom_cmd(model_name='llama3.2:3b'):
    """
    Initializes the application and starts the custom command prompt.

    Parameters:
    model_name (str): The model name to use for the API call. Defaults to 'llama3.2:3b'.
    """
    import platform
    os_name = platform.system()
    
    if os_name not in ['Windows', 'Darwin', 'Linux']:
        logging.error("Unsupported OS. This script is designed for Windows, macOS, and Linux.")
        print("Unsupported OS. This script is designed for Windows, macOS, and Linux.")
        return
    
    os_name_mapping = {
        'Darwin': 'MacOS',
        'Linux': 'Linux',
        'Windows': 'Windows'
    }
    
    os_name = os_name_mapping.get(os_name, 'Unsupported OS')
    
    custom_cmd(os_name, model_name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--spawn', action='store_true')
    parser.add_argument('--model', type=str, default='llama3.2:3b', help='Specify the model name to use')
    args = parser.parse_args()

    if not args.spawn:
        start_custom_cmd(args.model)
