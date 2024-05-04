import os
import time
import threading

from logging import Logger

from .libera_chat_watcher import LiberaChatWatcher
from .ycombinator_watcher import YCombinatorWatcher

from event_stream import EventStream

ACTIVE_WATCHERS = [LiberaChatWatcher, YCombinatorWatcher]

class WatchMan:
    """Manages all watchers."""
    WATCHERS = []
     
    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._event_stream = event_stream
        self._logging = logging
        self._config = config
        
        for Watcher in ACTIVE_WATCHERS:                   # instantiate active watchers
            self.WATCHERS.append(Watcher(event_stream=event_stream,
                                         config=config[Watcher.NAME], logging=logging))
    
    def deploy(self):
        """Deploy all watchers in watchers list."""
        for Watcher in self.WATCHERS:
            Watcher.start()
            self._logging.info(Watcher.NAME + ' watcher deployed.')
            
    # future method
    def terminate(self):
        """Terminate all currently deployed watchers."""
        return
