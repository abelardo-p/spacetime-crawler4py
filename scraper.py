import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tokenizer import tokenize

def scraper(url, resp):
    links = []
    if resp.status > 199 and resp.status < 300:
        next_links, cur_page_words = extract_link_information(url, resp)
        next_links = [link for link in next_links if is_valid(link)]
        return next_links, cur_page_words
        
    
def extract_link_information(url, resp) -> list[list[str], dict[str : int]]:
    soup = BeautifulSoup(resp.raw_response.content)
    tokenizer = tokenize(soup.stripped_strings)
    links = extract_next_links(url, resp, soup)
    return links, tokenizer.getTokens()

def extract_next_links(url, resp, soup):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    links = []
    transformUrl = lambda url : url.get('href').split('#')[0]
    return (transformUrl(link) for link in soup.find_all('a'))

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        domain = parsed.netloc.lower()
        valid_domains = ('ics.uci.edu', 
                         'cs.uci.edu', 
                         'informatics.uci.edu', 
                         'stat.uci.edu')
        if not any(domain.endswith(valid_dom) for valid_dom in valid_domains):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
