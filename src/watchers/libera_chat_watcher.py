import os
from datetime import datetime
from .base import WatcherBase

from events import NewsEvent
from event_stream import EventStream

from logging import Logger


class LiberaChatWatcher(WatcherBase):
    """Watches for file changes in liberachat log files."""
    NAME = 'libera'
    
    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._config = config[self.NAME]
        self._log_dir = self._config['path']
        self._targets = self._config['targets']
        self._event_stream = event_stream
        self._logging = logging
        self._file_handlers = []
        
    def start(self):
        """Start libera chat watchers."""
        path =  self._log_dir
        for target in self._targets:
            file_handler = FileHandler(filename=target, filepath=path, event_stream=self._event_stream,
                                       logging=self._logging)
            file_handler.retro_zorb()
            self._file_handlers.append(file_handler)
    
    def zorb(self, filename):
        for file_handler in self._file_handlers:
            if file_handler.filename == filename:
                file_handler.zorb_new_events()


class FileHandler:
    """Watches for file changes and adds new events to event stream."""
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
        """Triggered by watchdog. Adds new events to event stream."""
        with open(os.path.join(self._filepath, self._filename)) as file:
            lines = file.readlines()
            last_index = lines.index(self._lastline) + 1       # exclude last line
            for line in lines[last_index:]:
                try:
                    self.add(line)
                    self._lastline = line
                except ValueError:
                    continue
