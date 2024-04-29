from abc import ABCMeta, abstractmethod

class ArticleFetcher(metaclass=ABCMeta):
    """"""
    
    @abstractmethod
    def fetch_article(self, url: str):
        """Fetch article from given url."""
