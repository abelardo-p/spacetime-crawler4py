import re
import os
from urllib.parse import urlparse, urlunparse, urljoin
from bs4 import BeautifulSoup
from tokenizer import tokenize
from data import *
from pathlib import Path
import json 
# from typing import Tuple, List, Dict

DEBUG = True

def scraper(url: str, resp, stopWords: set[str]) -> tuple[list[str], dict[str, int], int]:
    next_links, cur_page_words, total_word_count = [], {}, 0

    if resp.status > 199 and resp.status < 300 and len(resp.raw_response.content) < RAW_RESPONSE_TEXT_LIMIT:
        next_links, cur_page_words, total_word_count = extract_link_information(url, resp, stopWords)
        invalid_page = check_page_low_data(cur_page_words, total_word_count)
        if invalid_page:
            next_links = []
        else:
            next_links = [link for link in next_links if is_valid(link, url)]

    if DEBUG: output_to_debug_file(resp, next_links, cur_page_words, total_word_count)
    return next_links, cur_page_words, total_word_count

def check_page_low_data(words_freqs, total_word_count):
    """Returns true if the links on this page should be skipped"""
    if total_word_count < MIN_TEXT_THRESHOLD:
        return True
    meaningful_word_count = sum(words_freqs.values())
    if meaningful_word_count / total_word_count < MEANINGFUL_WORDCOUNT_RATIO:
        return True
    return False

def extract_link_information(url, resp, stopWords) -> tuple[ list[str], dict[str, int], int]:
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    # What if the information successfully returned from site is not good
    tokenizer = tokenize(soup.stripped_strings, stopWords, countWords=True)
    links = extract_next_links(url, resp, soup)
    return links, tokenizer.getTokens(), tokenizer.getTotalWordCount()

def extract_next_links(url, resp, soup):
    links = []
    for tag in soup.find_all('a', href=True):
        href = tag['href'].split('#')[0]   # defragment
        abs_url = urljoin(resp.url, href)  # resolve relative paths
        links.append(abs_url)
    return links

def is_valid(url, parent_url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(php|css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        if len(url) > MAX_URL_LEN or (parsed.query and len(parsed.query.split('&')) > NUM_QUERY_PARAMS_THRESHOLD):
            return False
        
        subdomain = parsed.hostname
        valid_domains = ('ics.uci.edu', 
                         'cs.uci.edu', 
                         'informatics.uci.edu', 
                         'stat.uci.edu')
        
        if not subdomain or not any(subdomain.endswith(valid_dom) for valid_dom in valid_domains):
            return False
        CrawledData.subdomains[subdomain] += 1

        canonicalized_url = canonicalize(parsed)
        parent_url = canonicalize(parent_url)
        if canonicalized_url in CrawledData.visited:
            return False
        new_depth = CrawledData.visited[parent_url] + 1
        CrawledData.visited[canonicalized_url] = new_depth
        if new_depth > MAX_DEPTH:
            return False
        return True
 
    except TypeError:
        print ("TypeError for ", parsed)
        return False
    except ValueError:
        print ("ValueError for ", parsed)
        return False

def canonicalize(parsed):
    scheme = parsed.scheme.lower()
    netloc = parsed.hostname.lower()
    # Normalize path
    path = "/" + os.path.normpath(parsed.path).lstrip("/")
    # Sort query params
    query = "&".join(sorted(parsed.query.split("&"))) if parsed.query else ""
    return urlunparse((scheme, netloc, path, "", query, ""))

def output_to_debug_file(response, links, tokens, count):
    path = Path("./debug.txt")
    try: 
        with path.open(mode='a', encoding='utf-8', errors='replace') as file:
            scrape_data = {
                'url': response.url,
                'status': response.status,
                'links': links,
                'tokens': tokens,
                'count': count
            }
            json.dump(scrape_data, file)
            file.write('\n')
    except OSError:
        print(f"Could not open file: {path}")

