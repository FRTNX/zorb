import os
import time

import pickle
import threading

from events import NewsEvent, Event
from fetchers.mapper import get_fetcher

from logging import Logger

# todo: move to a utils file
def segment_data(data: list, segment_size: int):
    """Segment list in segments of size segment_size."""
    return [data[i:i + segment_size] for i in range(0, len(data), segment_size)]

class EventStream:
    """Container for Events. Also fetches articles for NewsEvents."""
    def __init__(self, logging: Logger, config: dict):
        self._events = []           # replace with other data structures for experiments
        self._logging = logging
        self._config = config
        
        if self._config['pickle']['auto_load']:     # load events from previous sessions
            self._load_pickle()
        
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
            if event.title == existing_event.title: # todo: find best containment conditions
                return True
        return False
    
    def events(self):
        """Return all events in event stream."""
        return [event.json() for event in self._events]
    
    def find_by_source(self, source: str):
        """Find events by source."""
        for event in self._events:
            if event.source == source:
                yield event

    def find_by_keyword(self, keyword: str):
        """Find events by keyword."""
        for event in self._events:
            if keyword.lower() in event.title.lower():
                yield event
                
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
        return sorted(sources.items(), key=lambda i: i[1], reverse=True)

    # uses threading to avoid bottleneck
    def add(self, event: NewsEvent, check_contains=True):
        """Add a new event to the event stream."""
        add_event_thread = threading.Thread(target=self._add_util, args=(event, check_contains))
        add_event_thread.start()
        
    def _add_util(self, event: Event, check_contains):
        """Utility function called from thread."""
        if check_contains:
            if self.__contains__(event):                     # event already exists, do nothing
                self._logging.info('Event already exists. Skipping: ' + event.title)
                return
        
        if type(event) == NewsEvent:
            if not event.article:                        # fetch news event article
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
    
    def _pickle(self):
        """Pickles the current event stream."""
        self._logging.info('Saving event stream...')
        pickle_file = os.path.join(self._config['pickle']['path'],
                                   self._config['pickle']['filename'])
        with open(pickle_file, 'wb') as f:
            pickle.dump(self._events, f)
        self._logging.info(f"Event stream saved successfully ({len(self)}).")
        
    def _load_pickle(self):
        """Loads pickled event stream from previous session. Typically called on instantiation."""
        def _load_pickled_events(segment):
            """Parallel process helper."""
            [self.add(event, False) for event in segment]

        self._logging.info('Loading pickled event stream...')
        pickle_file = os.path.join(self._config['pickle']['path'],
                                   self._config['pickle']['filename'])
        pickled_event_count = 0
        start = time.perf_counter()
        # split events and load in parallel
        with open(pickle_file, 'rb') as pickle_data:
            events = pickle.loads(pickle_data.read())
            pickled_event_count = len(events)
            if pickled_event_count > 1000:
                segment_size = 1000                      # let each thread handle 1000 events
                segments = segment_data(events, segment_size)
                self._logging.info(f'Processing {pickled_event_count} events on {len(segments)} threads.')
                threads = [threading.Thread(target=_load_pickled_events, args=(segment,)) for segment in segments]
                for thread in threads:
                    thread.start()
                    thread.join()
        stop = time.perf_counter()
        self._logging.info(f'Successfully loaded {pickled_event_count} pickled events in {stop-start} secs.')
            
    def _merge_pickles(self, directory: str):
        """Merge all pickles in directory."""
        for pickle_file in os.listdir(directory):
            event_stream_file = os.path.join(directory, pickle_file)
            with open(event_stream_file, 'rb') as pickle_data:         
                stream = pickle.loads(pickle_data.read())
                [self.add(event) for event in stream]
            
    def auto_save(self, interval=60):
        """Automatically pickle event stream every interval."""
        auto_save_thread = threading.Thread(target=self._auto_save_util, args=(interval,))
        auto_save_thread.start()
        
    def _auto_save_util(self, interval):
        """auto_save helper function."""
        while True:
            self._pickle()
            time.sleep(interval)
