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

def exact_match(tokens: list[str]):
    """Returns true if the page's contents are an exact match of a visited page"""
    hashed = hash_content(tokens)
    if hashed in CrawledData.page_hashes:
        return True
    CrawledData.page_hashes.add(hashed)
    return False

def near_match(tokens: list[str]):
    """ Returns true if the page's contents have a Jaccard Similarity score of at least 
    NEAR_SIMILARITY_THRESHOLD with any visited page's """
    grams = make_n_grams(tokens, N_GRAMS)
    for visited_page_grams in CrawledData.page_n_grams:
        sim_score = get_jaccard_similarity(grams, visited_page_grams)
        if sim_score > NEAR_SIMILARITY_THRESHOLD:
            return True
    CrawledData.page_n_grams.add(grams)
    return False