import requests
from bs4 import BeautifulSoup
import json
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import concurrent.futures

# Define params for random_user_agent.get_user_agent
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]       
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

# Get list of user agents.
user_agents = user_agent_rotator.get_user_agents()

def get_proxy_data(ip):
    url = f"https://scamalytics.com/ip/{ip.split(':')[0]}"
    user_agent = user_agent_rotator.get_random_user_agent()
    header = {'User-Agent': user_agent,
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 
              'Accept-Language': 'en-US,en;q=0.5', 
              'Accept-Encoding': 'gzip, deflate, br', 
              'Referer': 'https://scamalytics.com/', 
              'Connection': 'keep-alive', 
              'Upgrade-Insecure-Requests': '1',
              'Sec-Fetch-Dest': 'document',
              'Sec-Fetch-Mode': 'navigate',
              'Sec-Fetch-Site': 'same-origin',
              'Sec-Fetch-User': '?1'}
    resp = requests.get(url, headers=header)

    soup = BeautifulSoup(resp.text, 'html.parser')

    pre = soup.find('pre')
    table = soup.find('table')
    
    pre_text = pre.text.strip()
    basic_data = json.loads(pre_text)
    basic_data = {key.capitalize(): value.title() for key, value in basic_data.items()}
    full_data = {}

    for row in table.find_all('tr'):
        th_element = row.find('th')
        td_element = row.find('td')
    
        if th_element and td_element:
            header = th_element.get_text(strip=True)
            value = td_element.get_text(strip=True)
            full_data[header] = value

    proxy_data = {**basic_data, **full_data}
    return proxy_data

proxies = [ip.strip() for ip in open("proxies.txt","r")]

output_data_json_list = []

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(get_proxy_data, proxies)
    output_data_json_list.extend(results)

print(f"Finished Checking {len(output_data_json_list)} Proxies...\n\n\n")

for value in output_data_json_list:
    print(f'''Low Fraud Score Proxy: {value['Ip']}
Risk: {value['Score']}/100 ({value["Risk"]})
Hostname: {value["Hostname"]}
ASN: {value["ASN"]}
ISP Name: {value["ISP Name"]}
Organization Name: {value["Organization Name"]}
Connection type: {value["Connection type"]}
Country Name: {value["Country Name"]}
Country Code: {value["Country Code"]}
Region: {value["Region"]}
City: {value["City"]}
Postal Code: {value["Postal Code"]}
Metro Code: {value["Metro Code"]}
Area Code: {value["Area Code"]}
Latitude: {value["Latitude"]}
Longitude: {value["Longitude"]}
Anonymizing VPN: {value["Anonymizing VPN"]}
Tor Exit Node: {value["Tor Exit Node"]}
Server: {value["Server"]}
Public Proxy: {value["Public Proxy"]}
Web Proxy: {value["Web Proxy"]}
Search Engine Robot: {value["Search Engine Robot"]}\n\n\n\n''')
