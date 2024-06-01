# main.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from utilities.backup import backup_last_session
from utilities.branding import show_branding
from utilities.browser import *
from utilities.config import load_config, config
from utilities.query import *
from utilities.scanner import check_links_for_keywords
from utilities.search import *
from utilities.threads import calc_safe_threads, get_thread_id

# utilities.browser imports:
# print_green, print_red, print_blue from colored.py
# All functions from: errors.py
# random_proxy, valid_proxy, valid_type from proxy.py
# RecaptchaSolver() from recaptcha.py

def main():
    show_branding()
    backup_last_session()
    load_config()
    EXCLUDED_DOMAINS = config['EXCLUDED_DOMAINS']
    THREAD_COUNT = config['THREAD_COUNT']
    PROXY_TYPE = config['PROXY_TYPE']
    USER_AGENT = random_firefox_ua()
    RUN_VULN_SCAN = config['RUN_VULN_SCAN']
    SAFE_THREAD_COUNT = calc_safe_threads()

    # Load queries from queries.txt
    queries = load_queries()

    try:
        message = (
            f"Invalid thread count '{THREAD_COUNT}' provided in 'config.ini'. "
            f"Thread count must be a positive integer between 1-{SAFE_THREAD_COUNT}."
        )

        if THREAD_COUNT <= 0 or THREAD_COUNT >= SAFE_THREAD_COUNT:
            handle_failure_point(location=get_error_location(), task="checking thread count", error_string=message)
            exit()

    except Exception as e:
        handle_failure_point(location=get_error_location(), task="setting up thread count", e=e)
        exit()

    # Function to process each query
    def process_query(query_string):
        try:
            browser = None
            retries = 5
            attempts = 0
            
            while browser is None and attempts < retries:
                browser = initialize_browser(use_proxy=True, proxy_type=PROXY_TYPE, user_agent=USER_AGENT)
                attempts += 1
                if browser is None:
                    print_red(f"Failed to initialize browser, retrying...")
            
            if browser is None:
                return

            thread_id = f'Thread {str(get_thread_id())}'
            print_blue(f"[{thread_id}]: Processing query: {query_string}")

            # Part one
            first_search_operator = get_first_operator(query_string)
            first_dork_decoded = str(b'\x12\x0c', 'utf-8') + 'gws-wiz-serp"E' + first_search_operator

            # Part two
            inurl = inurl_queries(query_string)
            intext = intext_queries(query_string)
            ext = ext_queries(query_string)
            intitle = intitle_queries(query_string)
            site = site_queries(query_string)
            numrange = numrange_queries(query_string)
            after = after_queries(query_string)
            before = before_queries(query_string)
            negatives = negative_queries(query_string)
            operators_string_decoded = ' '.join(filter(None, [inurl, intext, ext, intitle, site, numrange, after, before, negatives]))

            gs_lp_string = get_gs_lp(first_dork_decoded, operators_string_decoded, first_search_operator)  # Google search location profile
            search_link = generate_search_link(query_string, gs_lp_string)

            # Make search request and process results
            response_text = get_search_response(browser, search_link, thread_id)

            if response_text == "swap proxy":
                print_blue(f"[{thread_id}]: Swapping proxy for query: {query_string}")
                proxy_swapped = swap_proxy(browser, PROXY_TYPE=PROXY_TYPE)
                if not proxy_swapped:
                    handle_failure_point("Unable to swap proxy, exiting application with links parsed")
                    return "break"
                solver = RecaptchaSolver()
                if solver.solveCaptcha(browser, thread_id) is False:
                    browser.quit()
                    print_red(f"[{thread_id}]: Failed to solve captcha.")

            extracted_hrefs = extract_hrefs(response_text)
            cleaned_links = clean_hrefs(extracted_hrefs, EXCLUDED_DOMAINS)
            print_green(f"[{thread_id}]: Finished processing query: {query_string} with {len(cleaned_links)} unique links")
            return query_string, cleaned_links
        except Exception as e:
            print_red(f"[{thread_id}]: Exception while processing query: {query_string} - {e}")
            return query_string, []
        finally:
            if browser is not None:
                close_browser(browser)

    # Process each query and collect results using multithreading
    all_cleaned_links = []
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        future_to_query = {executor.submit(process_query, query): query for query in queries}
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                query, cleaned_links = future.result()
                if cleaned_links == "break":
                    break
                all_cleaned_links.extend(cleaned_links)
                print_green(f"Query '{query}' returned {len(cleaned_links)} links")
            except Exception as exc:
                print_red(f"Query '{query}' generated an exception: {exc}")

    # Ensure all_cleaned_links has unique links
    unique_cleaned_links = list(set(all_cleaned_links))

    # Export all collected links
    export_links(unique_cleaned_links)

    if RUN_VULN_SCAN:
        check_links_for_keywords(unique_cleaned_links)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit()