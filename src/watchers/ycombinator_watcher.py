import time
import requests

import threading
from .base import WatcherBase

from events import NewsEvent
from event_stream import EventStream

from logging import Logger

class YCombinatorWatcher(WatcherBase):
    """"""
    NAME = 'ycombinator'
    
    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._event_stream = event_stream
        self._config = config
        self._logging = logging
        self._update_interval = 120
        
    def start(self):
        """Ineffective in this context. Here to meet base class requirements."""
        update_thread = threading.Thread(target=self._update)
        update_thread.start()
        return
    
    # future method
    def stop(self):
        """Stop watcher, stop threads, handle clean up."""
        return
        
    def zorb(self):
        """zorb YCombinator Hacker News."""
        self._logging.info('Fetching YCombinator Hacker News...')
        try:
            # todo: fetch more pages
            response = requests.get('http://hn.algolia.com/api/v1/search_by_date?page=1')
            response.raise_for_status()
            data = response.json()
            
            for item in data['hits']:
                title = item.get('story_title') if item.get('story_title') else item.get('title')
                article_url = item.get('story_url') if item.get('story_url') else item.get('url')
                if title and article_url:                     # invalid event, ignore         
                    event = NewsEvent(
                        title=title,
                        source=self.NAME,
                        article_url=article_url
                    )
                    self._event_stream.add(event)  
            self._logging.info('Updated YCombinator Hacker News.')
        except Exception as e:
            self._logging.error('Error fetching YCombinator Hacker News: ' + str(e))
            return
        
    def _update(self):
        """Update events every _update_interval."""
        while True:
            self.zorb()
            time.sleep(self._update_interval)
        