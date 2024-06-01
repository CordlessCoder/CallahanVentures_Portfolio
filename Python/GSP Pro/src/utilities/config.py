import configparser
import os
from pathlib import Path
from utilities.colored import *

config = {
    "EXCLUDED_DOMAINS": [],
    "THREAD_COUNT": 1,
    "PROXY_TYPE": "http",
    "RUN_VULN_SCAN": False
}

def get_parent_path():
    try:
        # Grabs the location of the current file (functions.py)
        functions_file_path = Path(__file__).resolve()
        
        # Get the directory where the current script exists
        utilities_directory = functions_file_path.parent
        
        # Grabs the parent directory of the child directory `utilities`
        parent_directory = utilities_directory.parent
        
        # Converts the parent directory path object to a string then returns it
        return str(parent_directory)
    
    except FileNotFoundError:
        print("Error: The current script file cannot be found.")
    except PermissionError:
        print("Error: Permission denied while accessing file or directory.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def get_config_path():
    parent_directory = get_parent_path()
    if parent_directory:
        return os.path.join(parent_directory, "config.ini")
    return None

def load_config():
    config_path = get_config_path()
    if not os.path.exists(config_path):
        print_red("Configuration file not found. Generating...")
        config_status = generate_config() # Returns True or False depending on success status.
        if not config_status: # Initializes constants with default settings in the event of a failed file generation
            print_red("An error occurred while attempting to generate a new configuration file")
            print_green("Continuing without config.ini, this will not affect the performance of the application.")
            config["EXCLUDED_DOMAINS"].extend(["google.com", "/search?client=", "/search?q="])
            return
    
    try:
        # Reads configuration settings
        config_parser = configparser.ConfigParser()
        config_parser.read(config_path)

        # Assigns configuration settings to constants
        config["EXCLUDED_DOMAINS"].extend([item.strip() for item in config_parser.get('SETTINGS', 'excluded_domains').split(',')])
        config["THREAD_COUNT"] = config_parser.getint('SETTINGS', 'thread_count', fallback=1)
        config["PROXY_TYPE"] = config_parser.get('SETTINGS', 'proxy_type', fallback='http')
        config['RUN_VULN_SCAN'] = config_parser.get('SETTINGS', 'run_vuln_scan', fallback=False)

        if config['RUN_VULN_SCAN'] == "True":
            config["RUN_VULN_SCAN"] = True
            
        elif config['RUN_VULN_SCAN'] == "False":
            config['RUN_VULN_SCAN'] = False
        
        else:
            print_red("Invalid value provided for 'run_vuln_scan' in 'config.ini', using default value 'False'")
            config['RUN_VULN_SCAN'] = False

        print_green("Successfully loaded configuration file!")
        return

    except configparser.NoSectionError as e:
        print_red(f"Error reading configuration file: {e}.\n\nGenerating new configuration file using the default settings.")
        config_status = generate_config() #returns True or False depending on success status.
        if config_status:
            load_config() #calls the function recursively in the event the generation is successful
            return

        if not config_status:
            print_red("An error occurred while attempting to generate a new configuration file")
            print_green("Continuing without config.ini, this will not affect the performance of the application.")
            config["EXCLUDED_DOMAINS"].extend(["google.com", "/search?client=", "/search?q="])
            return

    except Exception as e:
        print_red(f"Error reading configuration file: {e}.\n\nGenerating new configuration file using the default settings.")
        config_status = generate_config() #returns True or False depending on success status.
        if config_status:
            load_config() #calls the function recursively in the event the generation is successful
            return

        if not config_status:
            print_red("An error occurred while attempting to generate a new configuration file")
            print_green("Continuing without config.ini, this will not affect the performance of the application.")
            config["EXCLUDED_DOMAINS"].extend(["google.com", "/search?client=", "/search?q="])
            return

def generate_config():
    try:
        # Defines the configuration file path and contents
        config_path = get_config_path()
        config_file_contents = """[SETTINGS]
excluded_domains = google.com, /search?client=, /search?q=
thread_count = 1
proxy_type = http"""

        # Write the contents to the configuration file path
        with open(config_path, 'w') as config_file:
            config_file.write(config_file_contents)
        print_green("Configuration file generated successfully!")
        return True

    except Exception as e:
        print_red(f"Error generating configuration file\n{e}\nUsing default configuration settings.")
        return False
