import time
import requests
import threading

from .base import WatcherBase
from events import NewsEvent
from event_stream import EventStream

from logging import Logger


class YCombinatorWatcher(WatcherBase):
    """Watches for new YCombinator Hacker News events."""
    NAME = 'ycombinator'

    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._event_stream = event_stream
        self._config = config
        self._logging = logging
        self._update_interval = config['update_interval']
        self._active = False

    def start(self):
        """Starts _update thread that runs every update_interval."""
        self._active = True
        update_thread = threading.Thread(target=self._update)
        update_thread.start()

    def stop(self):
        """Stop watcher, stop threads, handle clean up."""
        self._active = False

    def zorb(self):
        """Absorb new YCombinator Hacker News events."""
        self._logging.info('Fetching YCombinator Hacker News...')
        data = []                                      # stores all relevant data across pages
        num_pages = self._config['num_pages']          # number of pages to fetch
        for page_number in range(1, num_pages + 1):    # pages are 1-indexed
            try:
                response = requests.get(f'http://hn.algolia.com/api/v1/search_by_date?page={page_number}')
                response.raise_for_status()
                response_data = response.json()
                data += response_data['hits']          # aggregate data from multiple pages
            except Exception as e:
                self._logging.error('Error fetching YCombinator Hacker News: ' + str(e))
                continue                               # in case error is localised to one request

        if len(data) > 0:
            for item in data:
                title = item.get('story_title') if item.get('story_title') else item.get('title')
                article_url = item.get('story_url') if item.get('story_url') else item.get('url')
                if title and article_url:              # invalid event, ignore
                    event = NewsEvent(
                        title=title,
                        source=self.NAME,
                        article_url=article_url
                    )
                    self._event_stream.add(event)  
            self._logging.info('Updated YCombinator Hacker News.')
            
    def _update(self):
        """Update events every _update_interval."""
        while self._active:
            self.zorb()
            time.sleep(self._update_interval)
