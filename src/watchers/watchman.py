from .libera_chat_watcher import LiberaChatWatcher
from event_stream import EventStream

ACTIVE_WATCHERS = [LiberaChatWatcher]

class WatchMan:
    """Manages all watchers."""
    
    WATCHERS = []
     
    def __init__(self, event_stream: EventStream, config: dict):
        self._event_stream = event_stream
        self._pw_mapper = { config[watcher]['path']: watcher for watcher in list(config) }
        print('pw_mapper:', self._pw_mapper)
        for watcher in ACTIVE_WATCHERS:
            self.WATCHERS.append(watcher(event_stream=event_stream, config=config))
    
    def deploy(self):
        """Deploy all watchers in watchers list"""
        for watcher in self.WATCHERS:
            watcher.start()
            print(watcher.NAME + 'watcher deployed.')
            
    def handle_change(self, watcher_name, filename):
        target_watcher = None
        for watcher in self.WATCHERS:
            if watcher.NAME == watcher_name:
                target_watcher = watcher
                
        if not target_watcher:
            raise ValueError('WTF bro.')

        watcher.zorb(filename)
    
    def watcher_by_path(self, path):
        return self._pw_mapper[path]
        


