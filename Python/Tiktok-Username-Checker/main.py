import concurrent.futures
import requests

keychecks = [
    '<p class="tiktok-nbjq96-PTitle emuynwa1">Couldn\'t find this account</p>',
    '<p class="tiktok-j62imk-PTitle emuynwa1">Couldn\'t find this account</p><p class="tiktok-13uasul-PDesc emuynwa2">Looking for videos? Try browsing our trending creators, hashtags, and sounds.</p></div>',
    '<p class="tiktok-13uasul-PDesc emuynwa2">Looking for videos? Try browsing our trending creators, hashtags, and sounds.</p>'
]

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
headers = {'User-Agent': user_agent}

not_taken = []

def check_username(username):
    r = requests.get(f"https://www.tiktok.com/@{username}", headers=headers)
    if any(keycheck in r.text for keycheck in keychecks):
        not_taken.append(username)
        print(f"Username: {username} is available")
    elif "<span>Videos</span>" in r.text:
        print(f"Username: {username} is taken")
    else:
        print(f"Unable to determine availability: {username}")

with open("usernames.txt", "r") as f:
    usernames = [username.strip() for username in f.readlines()]

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(check_username, usernames)

with open("available.txt", "a") as f2:
    for username in not_taken:
        f2.write(username + "\n")
