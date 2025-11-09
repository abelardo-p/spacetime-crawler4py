import hashlib
from data import *

def hash_content(tokens):
    joined = ' '.join(tokens)
    return hashlib.md5(joined.encode('utf-8')).hexdigest()

def make_n_grams(tokens, n=3):
    grams = {' '.join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}
    return grams

def get_jaccard_similarity(set1grams, set2grams):
    if not set1grams or not set2grams:
        return 0
    return len(set1grams & set2grams) / len(set1grams | set2grams)

"""Returns true if the page's contents are an exact match of a visited page"""
def exact_match(tokens: list[str]):
    hashed = hash_content(tokens)
    with CrawledData.lock:
        if hashed in CrawledData.page_hashes:
            return True
        CrawledData.page_hashes.add(hashed)
        return False

""" Returns true if the page's contents have a Jaccard Similarity score of at least 
    NEAR_SIMILARITY_THRESHOLD with any visited page's """
def near_match(tokens: list[str]):
    grams = make_n_grams(tokens, N_GRAMS)
    # Creating a copy to avoid locking during long Jaccard similarity computation
    with CrawledData.lock:
        visited_pages_copy = list(CrawledData.page_n_grams)

    for visited_page_grams in visited_pages_copy:
        sim_score = get_jaccard_similarity(grams, visited_page_grams)
        if sim_score >= NEAR_SIMILARITY_THRESHOLD:
            return True
            
    with CrawledData.lock: 
        CrawledData.page_n_grams.append(grams)
    return False
