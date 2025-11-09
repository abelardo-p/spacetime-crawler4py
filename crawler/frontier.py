import os
import shelve

from threading import Thread, Lock
from queue import Queue, Empty
from urllib.parse import urlparse
from utils import get_logger, get_urlhash, normalize
from scraper import is_valid
from data import *
import time

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = Queue()

        self.queue_lock = Lock()
        self.visited_lock = Lock()
        self.save_lock = Lock()
        self.politeness_lock = Lock()

        self.last_request_time = {
            "ics.uci.edu": 0.0,
            "cs.uci.edu": 0.0,
            "informatics.uci.edu": 0.0,
            "stat.uci.edu": 0.0
        }
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.put(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        try:
            with self.queue_lock:
                return self.to_be_downloaded.get()
        except IndexError:
            return None

    def add_url(self, url, parent_url=None):
        url = normalize(url)
        urlhash = get_urlhash(url)

        # Can add a lock here 
        if parent_url:
            with self.visited_lock:
                new_depth = CrawledData.visited.get(parent_url, 0) + 1
        else:
            new_depth = 0

        if new_depth > MAX_DEPTH:
            return
        with self.visited_lock:
            CrawledData.visited[url] = new_depth

        with self.save_lock:
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                self.save.sync()
                with self.queue_lock:
                    self.to_be_downloaded.put(url)
    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        with self.save_lock:
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {url}, but have not seen it before.")

            self.save[urlhash] = (url, True)
            self.save.sync()

    def wait_for_politeness(self, url, time_delay):
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return
        
        # find matching main domain
        for dom in self.last_request_time.keys():
            if hostname.endswith(dom):
                with self.politeness_lock:
                    elapsed = time.time() - self.last_request_time[dom]
                    if elapsed < time_delay:
                        time.sleep(time_delay - elapsed)
                    self.last_request_time[dom] = time.time()
                break