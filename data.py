from typing import ClassVar
from collections import Counter
from dataclasses import dataclass

@dataclass
class CrawledData:
    word_freqs: ClassVar[Counter[str]] = Counter()
    links_to_words : ClassVar[Counter[str]] = Counter()
    # using a separate set (visited) to also store urls of invalid urls
    visited: ClassVar[set[str]] = set()
    subdomains: ClassVar[Counter[str]] = Counter()