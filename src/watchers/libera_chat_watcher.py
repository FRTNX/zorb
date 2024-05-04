import os
import time

import threading

from datetime import datetime
from .base import WatcherBase

from events import NewsEvent
from event_stream import EventStream

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from logging import Logger

class LiberaChatWatcher(WatcherBase):
    """Watches for file changes in liberachat log files."""
    NAME = 'libera'
    
    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._config = config
        self._event_stream = event_stream
        self._logging = logging
        self._file_handlers = []
        
        self._logging.info(f'Instantiated libera watcher with config: {config}')
        
    def start(self):
        """Start libera chat watchers."""
        for target in self._config['targets']:
            file_handler = FileHandler(filename=target, filepath=self._config['path'],
                                       event_stream=self._event_stream, logging=self._logging)
            file_handler.retro_zorb()
            self._file_handlers.append(file_handler)
        watchdog_thread = threading.Thread(target=self._launch_observers)
        watchdog_thread.start()
        
    def stop(self):
        """Stop fetcher, stop watchdogs, handle clean up."""
        return
    
    def zorb(self, filename):
        """Absorb new events. Triggered when watchdog detects new logs."""
        for file_handler in self._file_handlers:
            if file_handler.filename == filename:
                file_handler.zorb_new_events()
                
    def _launch_observers(self):
        """Launch watchdog observers (typically from thread)."""
        self._logging.info('Launching watchdogs...')
        event_handler = FileModifiedEventHandler(watcher=self, config=self._config,
                                                 logging=self._logging)
        observer = Observer()
        observables = [
            {
                'name': 'libera',
                'handler': event_handler,
                'path': self._config['path']
            }
        ]
        for observable in observables:
            observer.schedule(observable['handler'], observable['path'])
        observer.start()
        
        try:
            while True:
                time.sleep(self._config['updateInterval'])
        finally:
            observer.unschedule_all()
            observer.stop()
            observer.join()

class FileHandler:
    """Watches for log file changes and adds new events to event stream."""
    
    def __init__(self, filename, filepath, event_stream, logging: Logger):
        self._filename = filename
        self._filepath = filepath
        self._event_stream = event_stream
        self._logging = logging
        self._lastline = None
        self._last_modified = datetime.now()
    
    @property
    def filename(self):
        return self._filename
    
    def add(self, log):
        tag, log = log.split('>') # todo: extract time stamp
        source, log = log.split(']')
        title, url = log.split('→')
        event = NewsEvent(
            title=title.strip(),
            source=source.replace('[', '').strip(),
            article_url=url.replace('\n', '').strip()
        )
        self._event_stream.add(event)

    def retro_zorb(self):
        """Adds existing libera logs to event stream."""
        with open(os.path.join(self._filepath, self._filename)) as logs:
            for log in logs.readlines():
                try:
                    self.add(log)
                    self._lastline = log
                except ValueError:
                    continue
                    
    def zorb_new_events(self):
        """Triggered by WatchMan. Adds new events to event stream."""
        with open(os.path.join(self._filepath, self._filename)) as file:
            lines = file.readlines()
            last_index = lines.index(self._lastline) + 1       # exclude last line
            for line in lines[last_index:]:
                try:
                    self.add(line)
                    self._lastline = line
                except ValueError:
                    continue

class FileModifiedEventHandler(FileSystemEventHandler):
    """Logs file modifications."""
    
    def __init__(self, watcher: WatcherBase, config: dict, logging: Logger):
        self._logging = logging
        self._watcher = watcher
        self._config = config

    def on_modified(self, event):
        # self._logging.info(f'Modified file: {event.src_path}')
        path, filename = os.path.split(event.src_path)
        if not event.is_directory and filename in self._config['targets']:            
            self._watcher.zorb(filename)
