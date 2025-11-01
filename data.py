from typing import ClassVar
from collections import Counter
from dataclasses import dataclass

seed_url = "http://www.ics.uci.edu"

RAW_RESPONSE_TEXT_LIMIT = 1 * 10 ** 6
MIN_TEXT_THRESHOLD = 50
MEANINGFUL_WORDCOUNT_RATIO = 0.35
MAX_DEPTH = 50
NUM_QUERY_PARAMS_THRESHOLD = 10


@dataclass
class CrawledData:
    word_freqs: ClassVar[Counter[str]] = Counter()
    links_to_words : ClassVar[Counter[str]] = Counter()
    # using a separate set (visited) to also store urls of invalid urls; values hold depth from seed
    visited: ClassVar[dict] = {seed_url: 0}
    subdomains: ClassVar[Counter[str]] = Counter()