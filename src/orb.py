class Orb:
    """EventStream adapter for querying event stream."""
    def __init__(self, event_stream):
        self._event_stream = event_stream
        
    def count(self):
        """Returns the number of events currently in the event stream."""
        return len(self._event_stream)
    
    def events_by_keyword(self, k):
        """Finds all events with keyword in title."""
        # eventually consider searching event body's for keyword
        for event in self._event_stream:
            if k in event.title:
                yield event.json()['title']
                
    def events_by_source(self, s):
        """Finds all events from source s."""
        for event in self._event_stream:
            if event.source == s:
                yield event.json()
