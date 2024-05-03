import os
import time
import threading

from logging import Logger

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
        # map paths to corresponding watchers
        self._path_watcher_mapper = { config[watcher]['path']: watcher for watcher in list(config) if config[watcher].get('path') }
        
        for watcher in ACTIVE_WATCHERS:
            self.WATCHERS.append(watcher(event_stream=event_stream, config=config, logging=logging))
    
    def deploy(self):
        """Deploy all watchers in watchers list."""
        for watcher in self.WATCHERS:
            watcher.start()
            self._logging.info(watcher.NAME + ' watcher deployed.')
        observer_thread = threading.Thread(target=self._launch_observers)
        observer_thread.start()
            
    def _launch_observers(self):
        """Launch watchdog observers (typically from thread)."""
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
    
    # todo: pperhaps specialise to exclusively cater for libera logs    
    def handle_change(self, watcher_name: str, filename: str):
        """Triggered by new events/file changes."""
        target_watcher = None
        for watcher in self.WATCHERS:
            if watcher.NAME == watcher_name:
                target_watcher = watcher
                break
                
        if not target_watcher:
            raise ValueError('Cannot find watcher:' + watcher_name)
        watcher.zorb(filename)
    
    def update(self, target: str):
        """Typically triggered by external cron job.
        
        Checks for new events at target source.
        """
        for watcher in self.WATCHERS:
            if watcher.NAME == target:
                # typically a watcher called by this update function has a
                # no-parameter zorb method, all details being worked out internally
                zorb_thread = threading.Thread(target=watcher.zorb)   # for the http
                zorb_thread.start()
                
    def auto_update(self):
        """Auto updates for supported watchers."""
        for watcher in list(self._config):
            if self._config[watcher].get('autoUpdate'):
                interval = self._config[watcher].get('updateInterval')
                auto_update_thread = threading.Thread(target=self._auto_update_util, args=(watcher, interval,))
                auto_update_thread.start()
        
    def _auto_update_util(self, target: str, interval: int = 120):
        """"""
        self._logging.info(f'Starting auto updates for watcher: {target}')
        while True:
            self.update(target)
            time.sleep(interval)
        
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
 