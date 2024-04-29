import requests


class ArticleFetcher:
    """"""


class GuardianFetcher(ArticleFetcher):
    """"""
    def _parse(self, html):
        """"""
        # make some beautiful soup!
        return html  # obviously return parsed result
    
    def fetch_article(self, url):
        response_data = requests.get(url)
        
        response_data.raise_for_status()
        html = response_data.content()
        
        result = self._parse(html)
        return result


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
    
    
class EventStream:
    """Container for NewsEvents.
    
    Fetches event articles for all new NewsEvents before adding them to some
    linked structure.
    """
    def __init__(self):
        self._events = []  # replace with other data structures for experiments
        
    def __getitem__(self, j):
        return self._events[j]
    
    def __iter__(self):
        for event in self._events:
            yield event
            
    def __len__(self):
        return len(self._events)

    def _fetch_article(self, source, article_url):
        """Fetches articles from various sources via specialised fetchers.
        
        Args:
            source (_type_): _description_
            article_url (_type_): _description_
        """
        if source == 'the guardian':
            fetcher = GuardianFetcher()
            article = fetcher.fetch_article(article_url)
            return article

    def add(self, event: NewsEvent):
        if type(event) == NewsEvent:
            if event.article_url:
                article = self._fetch_article(event.source, event.article_url)
                event.set_article(article)
            self._events.append(event)
        raise TypeError('Invalid type: ' + type(event))
    
    def find_by_source(self, source: str):
        for event in self._events:
            if event.source == source:
                yield event

    def find_by_keyword(self, keyword: str):
        for event in self._events:
            if keyword.lower() in event.title.lower():
                yield event


# todo: wrap in LiberaChat object
def parse(logfile):    
    with open(logfile, 'r') as logs:
        for log in logs.readlines():
            try:
                tag, log = log.split('>') # todo: extract time stamp
                source, log = log.split(']')
                title, url = log.split('→')
                
                event = NewsEvent(
                    title=title.strip(),
                    source=source.replace('[', '').strip(),
                    article_url=url.replace('\n', '').strip()
                )
                event_stream.add(event)
            except ValueError:
                continue


event_stream = EventStream()

most_active_sources = {
    'Google News - South Africa': 15,
    'Google News - US': 14,
    'Google News - US (Nation)': 12,
    'Google News - US Business': 6,
    'Newsweek': 7,
    'Reddit - /r/WorldNews - New': 6,
    'Rio Times - All': 5,
    'Slate - Main': 7,
    'SowetanLIVE': 7,
    'The Guardian - UK': 12,
    'The Hill - All News': 7,
    'Times of India - News (Video)': 8,
    'Wall Street Journal - World News': 5
}