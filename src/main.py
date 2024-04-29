import os
import time
import logging

from event_stream import EventStream
from watchers.watchman import WatchMan

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import config


logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='[zorb] %Y-%m-%d %H:%M:%S')

# the idea is to have a single event stream, imported where needed.
event_stream = EventStream()
     
watchman = WatchMan(event_stream=event_stream, config=config['watchers'])
watchman.deploy()


class FileModifiedEventHandler(FileSystemEventHandler):
    """Logs file modifications."""

    def on_modified(self, event):
        super().on_modified(event)
        if not event.is_directory:
            logging.info(f'Modified motherfucking file: {event.src_path}')
            path, filename = os.path.split(event.src_path)
            watcher_name = watchman.watcher_by_path(path)
            watchman.handle_change(watcher_name, filename)


if __name__ == '__main__':
    event_handler = FileModifiedEventHandler()
    observer = Observer()
    
    observables = [
        {
            'name': 'libera',
            'handler': event_handler,
            'path': config['watchers']['libera']['path']
        },
        {
            'name': 'decoy',
            'handler': event_handler,
            'path': config['watchers']['decoy']['path']
        }
    ]
    for observable in observables:
        logging.info('start watching directory {path}')
        observer.schedule(observable['handler'], observable['path'])
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    finally:
        observer.unschedule_all()
        observer.stop()
        observer.join()



