from threading import Thread
from data import CrawledData, output_stats
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from pathlib import Path
from tokenizer import tokenize

STOP_WORD_FILE = '../stopwords.txt'

class Worker(Thread):

    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

        self.stopWords = getStopWords(STOP_WORD_FILE)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls, cur_page_words, cur_page_word_count = scraper.scraper(tbd_url, resp, self.stopWords)
            CrawledData.word_freqs.update(cur_page_words)
            CrawledData.links_to_words[tbd_url] = cur_page_word_count
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        
        output_stats()


def getStopWords(path: str) -> dict[str]:
    stopWords = set()
    path = Path(path)
    try:
        with path.open(encoding='utf-8', errors='replace') as file:
            stopWordTokenizer = tokenize(file)
            stopWords.update(stopWordTokenizer.getTokens().keys())
    except OSError:
        print(f"Could not open file: {path}")
    finally:
        return stopWords