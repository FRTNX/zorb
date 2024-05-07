import time
import threading

from .base import WatcherBase
from .news_api import NewsAPI

from events import NewsEvent
from event_stream import EventStream

from logging import Logger

class AlJezeeraWatcher(WatcherBase):
    """Watches for new Al Jezeera events."""
    NAME = 'al_jezeera'
    
    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._event_stream = event_stream
        self._config = config
        self._logging = logging
        self._update_interval = config['update_interval']
        
    def start(self):
        """Start routine updates for new events."""
        update_thread = threading.Thread(target=self._update)
        update_thread.start()

    # future method
    def stop(self):
        """Stop All Jezeerah watcher, handle clean up."""
        return
            
    def zorb(self):
        """Absorb new Al Jezeera events."""
        self._logging.info('Updating Al Jezeera events...')
        news_api = NewsAPI()
        data = news_api.fetch_by_source(self._config['source_id'])
        
        for item in data:
            event = NewsEvent(
                title=item['title'],
                source=self.NAME,
                article_url=item['url']
            )
            self._event_stream.add(event)
        self._logging.info('Successfully update Al Jezeera events.')
        
    def _update(self):
        """Check for new events every _update_interval."""
        while True:
            self.zorb()
            time.sleep(self._update_interval)
                