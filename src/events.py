from abc import ABCMeta, abstractmethod

class Event(metaclass=ABCMeta):
    """Event base class."""
    
    @abstractmethod
    def json(self) -> dict:
        """Return event as dict."""


class NewsEvent(Event):
    """Captures a news event and its meta data.
    """
    def __init__(self, title: str, source: str, article_url: str):
        if not title or not source or not article_url:
            raise ValueError('Missing one or more required parameters.')   
        self._title = title
        self._source = source
        self._article_url = article_url
        self._article = None
        # todo: add formatted time, millis to help in ranged queries to EventStream
        
    @property
    def title(self):
        return self._title
    
    @property
    def source(self):
        return self._source
    
    @property
    def article_url(self):
        return self._article_url
    
    @property
    def article(self):
        return self._article
    
    def set_article(self, article):
        self.article = article
        
    def json(self):
        return {
            'title': self._title,
            'source': self._source,
            'article_url': self._article_url,
            'article': self._article
        }
