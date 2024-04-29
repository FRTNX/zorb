
class NewsEvent:
    """Captures a news event and its meta data.
    """
    def __init__(self, title: str, source: str, article_url: str):
        if not title or not source or not article_url:
            raise ValueError('Missing one or more required parameters.')
        
        self.title = title
        self.source = source
        self.article_url = article_url
        self.article = None
        # todo: add formatted time, millis to help in ranged queries to EventStream
        
    def set_article(self, article):
        self.article = article
        
    def json(self):
        return {
            'title': self.title,
            'source': self.source,
            'article_url': self.article_url,
            'article': self.article
        }
