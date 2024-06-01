from bs4 import BeautifulSoup
from utilities.colored import print_blue, print_green, print_red
from utilities.errors import get_error_location, handle_failure_point, handle_generic_error
from utilities.query import encode_query1, encode_query2, clean_query2, quote_plus #imports urlib.parse.quote_plus() from query.py
import requests

# Search utilities
def get_gs_lp(query1, query2, first_operator):
    """Cleans query 2 as its encoded counterpart requires the first operator removed,
    then encodes query1 and query2 in base64 before combining the b64 string"""
    try:
        query2_cleaned = clean_query2(first_operator, query2)
        query1_encoded = encode_query1(query1)
        query2_encoded = encode_query2(query2_cleaned)
        gs_lp_string = query1_encoded + query2_encoded
        if gs_lp_string:
            return gs_lp_string
        exit()
    except Exception as e:
        print(e)
        print("In get_gs_lp")
        exit()

def generate_search_link(query, gs_lp_string):
    link = "https://www.google.com/search?q="
    if query and gs_lp_string:
        # link += encode_query(query)
        link += quote_plus(query)
        link += "&client=firefox-b-d&sca_esv=d312657b286d9ff2&cs=1&biw=1760&bih=849&ei=bzhOZqu9Jfq3ptQPg6Ks6Aw&ved=0ahUKEwjrsJTl8KGGAxX6m4kEHQMRC80Q4dUDCBA&uact=5&gs_lp="
        link += gs_lp_string
        link += "&sclient=gws-wiz-serp#ip=1"
        return link
    else:
        print("Invalid Query Provided")
        exit()

def make_search_request(link, headers):
    try:
        response = requests.get(link, headers=headers)
        with open("debug.html", "w+", encoding='utf-8') as file:
            file.write(response.text)
        return response.text
    except Exception as e:
        pass

def extract_hrefs(content):
    try:
        location = "utilities.functions.extract_hrefs_from_response_content(content)" # Used for error handling
        task = "extracting hrefs from response content" # Used for error handling
        soup = BeautifulSoup(content, 'html.parser') # Parses the HTML content using BeautifulSoup
        hrefs = [a['href'] for a in soup.find_all('a', href=True)] # Extracts all hrefs found in response content
        if hrefs:
            return hrefs
        handle_failure_point("No href tags found, ensure your query is properly formatted and contains atleast two search operators.")

    except Exception as e:
        return []
        handle_generic_error(location, task, e)

def clean_hrefs(hrefs, excluded_domains):
    try:
        if hrefs is None:
            return []
        
        cleaned_hrefs = []
        for href in hrefs:
            # Excludes hrefs that dont start with the http/https and contain the excluded domains
            if any(href.startswith(protocol) for protocol in ["http", "https"]) and not any(domain in href for domain in excluded_domains):
                cleaned_hrefs.append(href)
        
        print_green(f"{len(hrefs)} links parsed!\n")
        return cleaned_hrefs
    except Exception as e:
        location = get_error_location()
        task = "extracting hrefs from response content"
        handle_generic_error(location, task, e)
        return []

def export_links(links):
    try:
        print_green(f"{len(links)} links parsed!\n")
        if len(links) > 0:
            print_blue("\nPlease wait while we export your links.")
            with open("links.txt", "w", encoding='utf-8') as file:
                for link in links:
                    file.write(link + '\n')
            return True
        else:
            print_red("0 links parsed, please ensure your queries are properly formatted and spelled correctly.")
            return False

    except Exception as e:
        location = get_error_location()
        task = "trying to export your links"
        handle_generic_error(location, task, e)
        return False
