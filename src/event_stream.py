from events import NewsEvent
from fetchers.mapper import get_fetcher

from logging import Logger

class EventStream:
    """Container for NewsEvents.
    
    Fetches event articles for all new NewsEvents before adding them to some
    sequence structure.
    """
    def __init__(self, logging: Logger):
        self._events = []  # replace with other data structures for experiments
        self._logging = logging
        
    def __getitem__(self, j):
        return self._events[j]
    
    def __iter__(self):
        for event in self._events:
            yield event
            
    def __len__(self):
        return len(self._events)

    def _fetch_article(self, source, article_url):
        """Fetches articles from various sources via specialised fetchers.
        """
        fetcher = get_fetcher(source)
        if not fetcher:
            return None
        
        article = fetcher.fetch_article(article_url)
        return article

    def add(self, event: NewsEvent):
        if type(event) == NewsEvent:
            if event.article_url:
                article = self._fetch_article(event.source, event.article_url)
                if article:
                    event.set_article(article)
            self._events.append(event)
            self._logging.info('Added new NewsEvent to EventStream: ' + event.json()['title'])
        else:
            raise TypeError('Invalid type: ' + type(event))
    
    def find_by_source(self, source: str):
        for event in self._events:
            if event.source == source:
                yield event

    def find_by_keyword(self, keyword: str):
        for event in self._events:
            if keyword.lower() in event.title.lower():
                yield event
