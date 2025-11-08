from typing import ClassVar
from collections import Counter
from dataclasses import dataclass
import pandas as pd
import os

seed_url = "http://www.ics.uci.edu"

RAW_RESPONSE_TEXT_LIMIT = 1 * 10 ** 6
MIN_TEXT_THRESHOLD = 50
MEANINGFUL_WORDCOUNT_RATIO = 0.35
MAX_DEPTH = 50

NUM_QUERY_PARAMS_THRESHOLD = 5
MAX_URL_LEN = 200

data_output_dir = './output'

@dataclass
class CrawledData:
    word_freqs: ClassVar[Counter] = Counter()
    links_to_words : ClassVar[Counter] = Counter()
    # using a separate set (visited) to also store urls of invalid urls; values hold depth from seed
    visited: ClassVar[dict] = {seed_url: 0}
    subdomains: ClassVar[Counter] = Counter()

def output_stats():
    word_freqs_df = pd.DataFrame.from_dict(CrawledData.word_freqs, orient='index', columns=['count'])
    word_freqs_df.to_csv(os.path.join(data_output_dir, 'total_word_frequencies.csv'))
    
    links_to_words_df = pd.DataFrame.from_dict(CrawledData.links_to_words, orient='index', columns=['count'])
    links_to_words_df.to_csv(os.path.join(data_output_dir, 'word_count_per_link.csv'))

    subdomains_df = pd.DataFrame.from_dict(CrawledData.subdomains, orient='index', columns=['count'])
    subdomains_df.to_csv(os.path.join(data_output_dir, 'subdomain_counts.csv'))

    
