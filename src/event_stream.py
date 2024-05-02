import os
import time

import pickle
import threading

from events import NewsEvent, Event
from fetchers.mapper import get_fetcher

from logging import Logger

class EventStream:
    """Container for Events.
    
    Fetches event articles for all new NewsEvents before adding them to some
    sequence/linked structure.
    """
    def __init__(self, logging: Logger, config: dict):
        self._events = []  # replace with other data structures for experiments
        self._logging = logging
        self._config = config
        
    def __getitem__(self, j):
        return self._events[j]
    
    def __iter__(self):
        for event in self._events:
            yield event
            
    def __len__(self):
        return len(self._events)
    
    # todo: get this working in logarithmic time, not the O(n) time used here
    def __contains__(self, event: Event) -> bool:
        """Returns True if event already exists in event stream."""
        for existing_event in self._events:
            if event.title == existing_event.title:
                return True
        return False

    # uses threading to avoid bottleneck
    def add(self, event: NewsEvent):
        """Add a new event to the event stream."""
        add_thread = threading.Thread(target=self._add_util, args=(event,))
        add_thread.start()
        
    def _add_util(self, event: Event):
        """Utility function called from thread."""
        # todo: validate event does not already exist
        if self.__contains__(event):                           # do nothing
            self._logging.info('Event already exists. Skipping: ' + event.title)
            return
        
        if type(event) == NewsEvent:
            if event.article_url:
                article = self._fetch_article(event.source, event.article_url)
                if article:
                    event.set_article(article)
            self._events.append(event)
            self._logging.info('Added new NewsEvent to EventStream: ' + event.json()['title'])
        else:
            raise TypeError('Invalid type: ' + type(event))
        
    def _fetch_article(self, source, article_url):
        """Fetches articles from various sources via specialised fetchers."""
        fetcher = get_fetcher(source)
        if not fetcher:
            return None
        
        article = fetcher.fetch_article(article_url)
        return article
    
    def events(self):
        """Return all events in event stream."""
        return [event.json() for event in self._events]
    
    def find_by_source(self, source: str):
        for event in self._events:
            if event.source == source:
                yield event

    def find_by_keyword(self, keyword: str):
        for event in self._events:
            if keyword.lower() in event.title.lower():
                yield event
                
    def pickle(self):
        self._logging.info('Saving event stream...')
        pickle_file = os.path.join(self._config['pickle']['path'],
                                   self._config['pickle']['filename'])
        with open(pickle_file, 'wb') as f:
            pickle.dump(list(self), f)
        self._logging.info("Event stream saved successfully.")
            
    def merge_pickles(self, directory: str):
        """Merge all pickles in directory dir."""
        for pickle_file in os.listdir(directory):
            event_stream_file = os.path.join(directory, pickle_file)
            stream = pickle.loads(event_stream_file)
            for event in stream:
                self.add(event)
            
    def auto_save(self, interval=60):
        """Automatically pickle event stream every interval."""
        auto_save_thread = threading.Thread(target=self._auto_save_util, args=(interval,))
        auto_save_thread.start()
        
    def _auto_save_util(self, interval):
        """Thread function that actually does the heavy lifting."""
        while True:
            self.pickle()
            time.sleep(interval)
            
    def source_count(self) -> dict:
        """Returns a dict where keys are sources and values are number of events
        from source.
        """
        sources = { }
        for event in self._events:
            if event.source in list(sources):
                sources[event.source] += 1
            else:
                sources[event.source] = 1
        return sorted(sources.items(), key=lambda x: x[1], reverse=True)
