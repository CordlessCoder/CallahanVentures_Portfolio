import requests
from urllib.parse import urlparse
import ctypes
from concurrent.futures import ThreadPoolExecutor

exposed_directories = []
visited_subdirectories = set()
blocked_count = 0
exposed_count = 0
error_count = 0
print_blocked_directories = False
print_error_links = False

def remove_uploads_suffix(url):
    if url.endswith("/uploads"):
        return url[:-7]
    else:
        return url

def set_cmd_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def extract_directories_with_url(url):
    if "google.com" not in url:
        parsed_url = urlparse(url)
        directories = parsed_url.path.split('/')
        number_of_directories = len(directories)
        
        if number_of_directories > 2:  # Ensure there are more than two directories
            shortened_directories = directories[1:-1]
            shortened_urls = [f"{parsed_url.scheme}://{parsed_url.netloc}/{'/'.join(shortened_directories[:i+1])}/" for i in range(len(shortened_directories))]
            return shortened_urls
        else:
            return [url]
    return ["Google Url"]

def check_directory_exposure(url):
    global blocked_count, exposed_count, error_count, print_blocked_directories

    try:
        response = requests.get(url, timeout=10)
        if 'Index of' in response.text:
            print(f"Exposed Directory: {url}")
            exposed_directories.append(url)
            exposed_count += 1
        
        elif response.status_code == 403 or 'Forbidden' in response.text:
            if print_blocked_directories:
                print(f"Directory Blocked (Forbidden): {url}")
            blocked_count += 1
        
        elif "404" in response.text or 'Not Found' in response.text or 'Página no encontrada' in response.text:
            if print_blocked_directories:
                print(f"Directory Blocked (Not Found): {url}")
            blocked_count += 1

        else:
            if print_blocked_directories:
                print(f"Directory Blocked: {url}")
            blocked_count += 1

    except requests.RequestException as e:
        if print_error_links:
            print(f"Error checking {url}\n\n")
        error_count += 1

def process_url(base_url):
    global blocked_count, exposed_count, error_count

    directories = extract_directories_with_url(base_url)
    if directories:
        for full_url in directories:
            if full_url not in visited_subdirectories:
                visited_subdirectories.add(full_url)
                check_directory_exposure(full_url)
                set_cmd_title(f"Exposed: {exposed_count} | Blocked: {blocked_count} | Errors: {error_count}")

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            urls = file.readlines()
            with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as per your requirement
                executor.map(process_url, urls)
    except FileNotFoundError:
        print("Please Make Sure links.txt Is Present.")
    finally:
        set_cmd_title("Script Completed")

# Get user input
print_blocked_input = input("Do you want to print blocked directories? (y/n): ")
print_blocked_directories = print_blocked_input.lower() == 'y'

print_error_links_input = input("Do you want to print links with request errors? (y/n): ")
print_error_links = print_error_links_input.lower() == 'y'

file_path = 'links.txt'
process_file(file_path)
print(f'{len(exposed_directories)} Exposed Directories Found, Writing To File.')
with open('exposed directories.txt', 'w+') as file:
    for directory in exposed_directories:
        file.write(f'{directory}\n')

print("Finished.")
