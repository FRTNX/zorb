import os
import time
import threading

from logging import Logger

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .libera_chat_watcher import LiberaChatWatcher
from event_stream import EventStream

ACTIVE_WATCHERS = [LiberaChatWatcher]

class WatchMan:
    """Manages all watchers."""
    WATCHERS = []
     
    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._event_stream = event_stream
        self._logging = logging
        self._config = config
        self._path_watcher_mapper = { config[watcher]['path']: watcher for watcher in list(config) }
        
        for watcher in ACTIVE_WATCHERS:
            self.WATCHERS.append(watcher(event_stream=event_stream, config=config, logging=logging))
    
    def deploy(self):
        """Deploy all watchers in watchers list"""
        for watcher in self.WATCHERS:
            watcher.start()
            self._logging.info(watcher.NAME + ' watcher deployed.')
        observer_thread = threading.Thread(target=self._launch_observers)
        observer_thread.start()
            
    # launch from thread
    def _launch_observers(self):
        event_handler = FileModifiedEventHandler(self._logging, self)
        observer = Observer()

        observables = [
            {
                'name': 'libera',
                'handler': event_handler,
                'path': self._config['libera']['path']
            }
        ]
        for observable in observables:
            observer.schedule(observable['handler'], observable['path'])
        
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        finally:
            observer.unschedule_all()
            observer.stop()
            observer.join()
            
    def handle_change(self, watcher_name: str, filename: str):
        """Triggered by new events/file changes."""
        target_watcher = None
        for watcher in self.WATCHERS:
            if watcher.NAME == watcher_name:
                target_watcher = watcher
                
        if not target_watcher:
            raise ValueError('Cannot find watcher:' + watcher_name)

        watcher.zorb(filename)
    
    def watcher_by_path(self, path: str):
        """Return the watcher observing the specified path."""
        return self._path_watcher_mapper[path]


class FileModifiedEventHandler(FileSystemEventHandler):
    """Logs file modifications."""
    def __init__(self, logging: Logger, watchman: WatchMan):
        # super().__init__()
        self._logging = logging
        self._watchman = watchman

    def on_modified(self, event):
        super().on_modified(event)
        if not event.is_directory:
            self._logging.info(f'Modified file: {event.src_path}')
            path, filename = os.path.split(event.src_path)
            watcher_name = self._watchman.watcher_by_path(path)
            self._watchman.handle_change(watcher_name, filename)
 