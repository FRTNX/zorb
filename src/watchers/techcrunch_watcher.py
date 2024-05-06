# events
import time
import requests

import threading
from .base import WatcherBase

from events import NewsEvent
from event_stream import EventStream

from logging import Logger

HEADERS = {
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
    'X-TC-EC-Auth-Token': '',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json; charset=utf-8',
    'Referer': 'https://techcrunch.com/',
    'X-TC-UUID': '',
    'sec-ch-ua-platform': '"Linux"',
}

class TechCrunchWatcher(WatcherBase):
    """TechCrunch watcher."""
    NAME = 'techcrunch'
    
    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._event_stream = event_stream
        self._config = config
        self._logging = logging
        self._update_interval = config['update_interval']
        
    def start(self):
        """Starts TechCrunch _update thread, run every update_interval."""
        update_thread = threading.Thread(target=self._update)
        update_thread.start()
        return
    
    # future method
    def stop(self):
        """Stop TechCrunch watcher, threads, handle clean up."""
        return
        
    def zorb(self):
        """Absorb new TechCrunch events."""
        self._logging.info('Fetching TechCrunch events...')
        data = []
        num_pages = self._config['num_pages']
        for page_number in range(1, num_pages + 1):
            try:
                params = {
                    'page': str(page_number),
                    '_embed': 'true',
                    'es': 'true',
                    'cachePrevention': '0',
                }
                response = requests.get('https://techcrunch.com/wp-json/tc/v1/magazine', params=params, headers=HEADERS)
                response.raise_for_status()
                response_data = response.json()
                
                # techcrunch response jsons are massive. only selecting what we need
                # so as not to keep bloat data in memory.
                target_attributes = [
                    {
                        'title': item['yoast_head_json']['og_title'],    # cleaner than item['title']
                        'article_url': item['link']
                    }
                    for item in response_data                            # comprehension go brrr
                ]
                data += target_attributes
                # todo: consider time.sleep here to avoid being blocked by techcrunch servers
            except Exception as e:
                self._logging.error('Error fetching TechCrunch events: ' + str(e))
                continue
        
        if len(data) > 0:
            for item in data:
                event = NewsEvent(
                    title=item['title'],
                    source=self.NAME,
                    article_url=item['article_url']
                )
                self._event_stream.add(event)  
            self._logging.info('Updated TechCrunch events.')
        
    def _update(self):
        """Update TechCrunch events every _update_interval."""
        while True:
            self.zorb()
            time.sleep(self._update_interval)
