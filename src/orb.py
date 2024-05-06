
class Orb:
    """EventStream adapter providing (only) read access."""
    def __init__(self, event_stream):
        self._event_stream = event_stream
        
    def count(self):
        """Returns the number of events currently in the event stream."""
        return len(self._event_stream)
    
    def events(self):
        """Returns all events."""
        return self._event_stream.events()
    
    def events_by_keyword(self, k):
        """Finds all events with keyword in title."""
        return self._event_stream.find_by_keyword(k)
                
    def events_by_source(self, s):
        """Finds all events from source s."""
        return self._event_stream.find_by_source(s)
    
    def sources(self):
        return self._event_stream.source_count()
