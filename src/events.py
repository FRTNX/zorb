from abc import ABCMeta, abstractmethod
from datetime import datetime

class Event(metaclass=ABCMeta):
    """Event base class."""
    
    @abstractmethod
    def json(self) -> dict:
        """Return event as dict."""

class NewsEvent(Event):
    """Captures a news event and its meta data."""
    
    def __init__(self, title: str, source: str, article_url: str, creation=None):
        """Initialise a new news event.

        Args:
            title (str): Event title/headline.
            source (str): The watcher that absorbed the event.
            article_url (str): To be used by fetchers later.
            creation (date, optional): Event creation date from external source. Defaults to None.

        Raises:
            ValueError: On missing required params.
        """
        if not title or not source or not article_url:
            raise ValueError('Missing one or more required parameters.')   
        self._title = title
        self._source = source
        self._article_url = article_url
        self._article = None
        self._created = datetime.now()
        self._updated = None
        self._creation = creation if creation else self._created
        
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
            'article': self._article,
            'created': self._created,
            'updated': self._updated,
            'creation': self._creation
        }
